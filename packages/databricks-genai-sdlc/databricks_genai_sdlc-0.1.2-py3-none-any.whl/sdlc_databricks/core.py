import requests
import json
import os
import re
import fitz  # PyMuPDF
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType
import pandas as pd
from pyspark.sql import SparkSession
import logging
import time
import re
from collections import defaultdict
import time


class SDLC_DATABRICKS():
    def __init__(self, 
                 GITHUB_API, 
                 GITHUB_REPO, 
                 GITHUB_TOKEN, 
                 FILE_PATH, 
                 GITHUB_BRANCH,
                 DOC_GENERATOR_MODEL = None,
                 CODE_GENERATOR_MODEL = None,
                 DATABRICKS_PAT=None, 
                 WORKSPACE_URL=None,
                 GITHUB_USERNAME=None,
                 LANGUAGE=None
                 ):
        self.GOOGLE_API_KEY= ""
        self.GITHUB_USERNAME= GITHUB_USERNAME
        self.GITHUB_TOKEN= GITHUB_TOKEN
        self.FILE_PATH = FILE_PATH
        self.GITHUB_API = GITHUB_API
        self.GITHUB_REPO = GITHUB_REPO
        self.GITHUB_TOKEN = GITHUB_TOKEN
        self.FILE_PATH = FILE_PATH
        self.GITHUB_BRANCH = GITHUB_BRANCH
        self.active_model = ""
        self.DOC_GENERATOR_MODEL = DOC_GENERATOR_MODEL
        self.CODE_GENERATOR_MODEL = CODE_GENERATOR_MODEL
        self.MODEL_NAME = ""
        self.LANGUAGE = LANGUAGE
        self.MODE = "mosaic"
        self.DATABRICKS_PAT = DATABRICKS_PAT
        self.WORKSPACE_URL = WORKSPACE_URL
        self.spark = SparkSession.builder.appName("SDLC_DATABRICKS").getOrCreate()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)


    def generate_response(self, prompt):
        self.logger.info(f"Generating response using mode: {self.MODE}")
        
        if self.MODE == "default":
            # Gemini Models (Default)
            models = [
                "gemini-2.0-flash",  # Primary
                "gemma-3n-e4b-it"    # Fallback
            ]
            
            for model in models:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.GOOGLE_API_KEY}"
                headers = {"Content-Type": "application/json"}
                payload = {
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                }

                for attempt in range(3):
                    try:
                        response = requests.post(url, headers=headers, json=payload)
                        self.logger.info(f"{model} - Attempt {attempt+1} - Status Code: {response.status_code}")

                        if response.status_code == 200:
                            response_text = response.json()['candidates'][0]['content']['parts'][0]['text']
                            self.llm_response = response_text
                            self.active_model = model
                            self.logger.info(f"Successfully received response from {model}")
                            return self.llm_response
                        else:
                            self.logger.warning(f"{model} - Attempt {attempt+1} failed. Retrying in 5 seconds...")
                            time.sleep(5)

                    except Exception as e:
                        self.logger.error(f"Exception with {model} - Attempt {attempt+1}: {str(e)}")
                        time.sleep(5)

            self.logger.error("All Gemini models failed.")
            return None

        elif self.MODE == "mosaic":
            # Databricks Model Invocation
            if not all([self.MODEL_NAME, self.DATABRICKS_PAT, self.WORKSPACE_URL]):
                self.logger.error("Databricks MODEL_NAME, PAT, and WORKSPACE_URL are required for 'mosaic' mode.")
                return None

            url = f"{self.WORKSPACE_URL}/serving-endpoints/{self.MODEL_NAME}/invocations"
            headers = {
                "Authorization": f"Bearer {self.DATABRICKS_PAT}",
                "Content-Type": "application/json"
            }
            payload = {
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

            for attempt in range(3):
                # try:
                response = requests.post(url, headers=headers, json=payload)
                self.logger.info(f"MosaicAI model {self.MODEL_NAME} - Attempt {attempt+1} - Status Code: {response.status_code}")
                # print(response.json())

                if response.status_code == 200:
                    response_text = response.json()["choices"][0]["message"]["content"]
                    self.llm_response = response_text
                    self.active_model = self.MODEL_NAME
                    self.logger.info(f"Successfully received response from {self.MODEL_NAME}")
                    return self.llm_response
                else:
                    self.logger.warning(f"{self.MODEL_NAME} - Attempt {attempt+1} failed. Retrying in 5 seconds...")
                    time.sleep(5)

                # except Exception as e:
                #     self.logger.error(f"Exception with {self.MODEL_NAME} - Attempt {attempt+1}: {str(e)}")
                #     # print(f"Exception with {self.MODEL_NAME} - Attempt {attempt+1}: {str(e)}")
                #     time.sleep(5)

            self.logger.error(f"Databricks model {self.MODEL_NAME} failed after 3 attempts.")
            return None

        else:
            self.logger.error("Invalid mode specified. Choose 'default' or 'mosaic'.")
            return None


    def pdf_extractor(self):
        self.logger.info("##---STEP-1: Extracting PDF content.---##")
        try:
            df_pdf = self.spark.read.format("binaryFile").load(self.FILE_PATH)

            @pandas_udf(StringType())
            def extract_text_udf(content_series: pd.Series) -> pd.Series:
                texts = []
                for content in content_series:
                    try:
                        with fitz.open(stream=content, filetype="pdf") as doc:
                            text = "\n".join([page.get_text() for page in doc])
                        texts.append(text)
                    except Exception as e:
                        texts.append(f"ERROR: {e}")
                return pd.Series(texts)

            df_with_text = df_pdf.withColumn("text", extract_text_udf("content"))

            # Fix: use collect instead of rdd
            all_text_list = [row.text for row in df_with_text.select("text").collect()]
            self.all_pdf_text = "\n".join(all_text_list)

            self.logger.info("Successfully extracted PDF content.")
            return self.all_pdf_text
        except Exception as e:
            self.logger.error(f"Error while extracting content from PDF: {str(e)}")


    def func_prompt(self, general_text):
        func_prompt = f"""
                        You are a business analyst. Convert the following general software requirement into a detailed Functional Requirement Document (FRD).

                        Use this Business Requirement Document(BRD) to construct a detailed human like functional requirement document. Write the requirements in bullet point.
                        Adhere to the text present only in the BRD's "Coding Requirements" section. Donot use any other sections to create functional requirement.

                        \"\"\"
                        {general_text}
                        \"\"\"

                        Follow the following functional requirement template:

                        1. Requirement ID
                        FR-<ModuleAbbreviation>-<SequentialNumber>
                        E.g., FR-INV-001

                        2. Title
                        A brief and descriptive title of the functionality.
                        E.g., "Generate Monthly Invoice Reports"

                        3. Description
                        A concise explanation of the business functionality or feature required.
                        E.g., "The system must generate monthly invoice reports for each active customer based on billing data from the previous month."

                        4. Preconditions
                        List all conditions that must be true before this function can be executed.
                        E.g., "Customer must have an active subscription; billing data must be available for the month."

                        5. Main Flow / Functional Steps
                        Step-by-step explanation of how the function behaves, from trigger to completion.
                        E.g.,

                        System retrieves all active customer accounts.

                        Pulls relevant billing data for each account.

                        Generates PDF reports.

                        Stores reports in secure location.

                        Sends email notification to customers with report link.

                        """
        return func_prompt
                    
    def tech_prompt(self, functional_output):
        tech_prompt = f"""
                        You are a software architect. Based on the following general requirement, generate a **Technical Requirement Document (TRD)**. The TRD should include:

                        Use the Functional Requirement Document(FRD) to construct a detailed human like technical requirement document. Write the requirements in bullet point.
                        Adhere to the text present only in the FRD. Donot simply copy paste the following template, provide the details in every pointers wrt FRD. Fill <provide> section dynamically wrt FRD requirements. Donot create any tables, write everything in pointers. Write very concise text to avoid over token consumption.

                        \"\"\"
                        {functional_output}
                        \"\"\"

                        Follow the following functional requirement template:

                        1. Technical Requirement ID
                        TR-<ModuleAbbreviation>-<SequentialNumber>
                        E.g., TR-INV-001

                        2. Related Functional Requirement(s)
                        Reference the corresponding FR IDs.
                        E.g., FR-INV-001

                        3. Objective
                        A one liner technical interpretation of what needs to be built.
                        E.g., "Implement a PySpark job to aggregate monthly customer billing data and generate output in Parquet and PDF format."

                        4. Target Cluster Configuration
                        Indicate the Databricks cluster where the job will run.

                        Cluster Name: <provide>

                        Databricks Runtime Version: <provide>

                        Node Type: <provide>

                        Driver Node: <provide>

                        Worker Nodes: <provide>

                        Autoscaling: <provide>

                        Auto Termination: <provide>

                        Libraries Installed: <provide>

                        5. Source Data Details <provide>
                        Dataset Name	Location (Path/Table)	Format	Description
                        
                        6. Target Data Details <provide>
                        Output Name	Location	Format	Description
                        
                        7. Job Flow / Pipeline Stages
                        <provide>

                        8. Data Transformations / Business Logic
                        Step	Description	Transformation Logic
                        <provide>

                        9. Error Handling and Logging
                        <provide>

                        """
        return tech_prompt

    def functional_document(self):
        self.logger.info("\n##---STEP-2: Generating functional document.---##")
        try:
            self.MODEL_NAME = self.DOC_GENERATOR_MODEL
            # Check if PDF text is already extracted
            if not hasattr(self, 'all_pdf_text') or not self.all_pdf_text:
                self.pdf_extractor()
            else:
                self.logger.info("PDF text already extracted.")

            # Generate functional requirement
            self.functional_output = self.generate_response(self.func_prompt(self.all_pdf_text))
            self.logger.info("Successfully generated functional document.")
            return self.functional_output

        except Exception as e:
            self.logger.error(f"Error while generating functional document: {str(e)}")


    def technical_document(self):
        self.logger.info("\n##---STEP-3: Generating technical document.---##")
        try:
            self.MODEL_NAME = self.DOC_GENERATOR_MODEL
            # Check if PDF text is already extracted
            if not hasattr(self, 'all_pdf_text') or not self.all_pdf_text:
                self.pdf_extractor()
            else:
                self.logger.info("PDF text already extracted.")

            # Generate technical requirement
            self.pdf_extractor()
            self.technical_output = self.generate_response(self.tech_prompt(self.functional_output))
            self.logger.info("Successfully generated technical document.")
            return self.technical_output
        except Exception as e:
            self.logger.error(f"Error while generating technical document: {str(e)}")

    def generate_pyspark_code(self):
        self.logger.info("\n##---STEP-4: Generating pyspark code.---##")
        try:
            """
            Generate PySpark code dynamically based on the functional and technical requirements using GenAI.
            """
            self.MODEL_NAME = self.CODE_GENERATOR_MODEL
            # Check if PDF text is already extracted
            if not hasattr(self, 'technical_output') or not self.technical_output:
                self.technical_document()
            else:
                self.logger.info("Technical document present.")
            
            python_prompt = f"""
                You are a senior software engineer specializing in Databricks, PySpark, and scalable enterprise data engineering systems.
 
                Your task: Generate **production-quality PySpark code** based strictly on the technical requirements below:
                {self.all_pdf_text}
 
                Follow these key instructions:
 
                1. General:
                - Do **not** create logic or schemas not mentioned in the requirement.
                - Use PySpark DataFrame APIs (`spark.read`, `withColumn`, `filter`, `groupBy`, etc.).
                - Use `inferSchema` when loading data if schema has not been given.
                - Ensure the code scales for large datasets and includes relevant transformation/cleaning/aggregation logic.
 
                2. Coding Standards:
                - Use clean, realistic names (avoid "foo", "bar", or Hello World).
                - Combine config and logic in one file unless strong justification to split.
                - Use functions/classes/modules if it improves clarity, but avoid unnecessary fragmentation.
                - If joins are used, make sure ambiguous key errors should not occur.
                - Imports should be Databricks-friendly: use relative or top-level imports only (e.g., `from module1 import func`).
                - Simulate external integrations (APIs, databases, storage) when required.
                - Generate minimal working code that implements the technical requirements. Do not generate boilerplate code.
                - Output only essential code needed for functionality.
 
                3. Testing:
                - Include realistic test cases with sample data.
                - Use `pytest` or `unittest` for tests. Ensure they are runnable in a Databricks environment.
                - Generate minimal but meaningful mock datasets if needed for testing.
 
                4. Output Directory:
                Follow this exact structure. Generate all required files:
                project_name/
                │
                ├── src/
                │   ├── __init__.py
                │   ├── module1.py
                │   └── module2.py
                │
                ├── tests/
                │   ├── test_module1.py
                │   └── test_module2.py
                │
                ├── data/                # Sample input data (if applicable)
                ├── requirements.txt     # List only required packages
                ├── pyproject.toml       # Include project name, version, description, authors
                ├── README.md            # Project overview, setup, usage, sample commands
                ├── LICENSE
                └── .gitignore
 
                5. Output Format:
                Each file should be output in this format:
                ===================path:<relative_path>====================
                <code>
                ===================path:end================================
 
                6. Validation:
                Cross-check the generated code against the technical requirements for completeness and correctness before finalizing.
                """  

            sql_prompt = f"""
                You are a senior software engineer specializing in Databricks, SQL, and scalable enterprise data engineering systems.

                Your task: Generate **production-quality SQL queries** based strictly on the technical requirements below:
                {self.all_pdf_text}

                
                Important Instructions:
                - Only generate SQL and SparkSQL code that can be executed in a Databricks notebook using `%sql` cells.
                - Do **not** generate Python (`.py`) code, pseudocode, or any other programming language.
                - Each SQL query must be wrapped in the following Databricks notebook cell format:

                %sql
                select * from <database>.<table_name>
                where <condition>;


                1. Output Format:
                - Save **validation SQL queries* to a single file in the folder: `sqlvalidation_queries/`
                - Save **SparkSQL queries** to a single file in the folder: `sparksql_queries/`
                - Use the following output format for each file:
                ===================path:<relative_path>====================
                <code>
                ===================path:end================================

                2. Validation:
                Cross-check the generated code against the technical requirements for completeness and correctness before finalizing.
                """         
            if self.LANGUAGE == 'SQL':      
                return self.generate_response(prompt=sql_prompt)
            else:
                return self.generate_response(prompt=python_prompt)
        except Exception as e:
            self.logger.error(f"Error while generating pyspark code: {str(e)}")


    def parse_llm_output(self):
        self.logger.info("Parsing LLM output, generating code directory.")
        try:
            pattern = re.compile(r"=+path:(.*?)=+\n(.*?)(?=\n=+path:|\Z)", re.DOTALL)
            matches = pattern.findall(self.llm_response)
            self.llm_parser = {path.strip(): content.strip() for path, content in matches}
            self.logger.info("Successfully parsed LLM output.")
            return self.llm_parser 
        except Exception as e:
            self.logger.error(f"Error during parsing: {str(e)}")

    def clean_files_dict(self):
        self.logger.info("Cleaning code directory.")
        try:
            self.cleaned = {}
            for path, content in self.llm_parser.items():
                # Remove leading './' if present
                clean_path = path.lstrip("./")

                # Remove markdown triple backticks and language tags from content
                # Regex removes ```python or ``` and closing ```
                content_clean = re.sub(r"^```[a-zA-Z]*\n", "", content)  # Remove opening ```
                content_clean = re.sub(r"```$", "", content_clean)       # Remove closing ```
                
                self.cleaned[clean_path] = content_clean
                self.logger.info("Successfully cleaned code directory.")
            return self.cleaned
        except Exception as e:
            self.logger.error(f"Error during code directory cleaning: {str(e)}")

    def github_api_headers(self):
        return {
            "Authorization": f"token {self.GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json",
        }

    def push_to_github(self, commit_message="Initial commit by library"):
        self.logger.info("\n##---STEP-5: Github process started---##")
        if not self.GITHUB_TOKEN:
            return False, "GitHub token is not set. Please set GITHUB_TOKEN environment variable."

        try:
            # Step 1: Generate documents
            func_text = self.functional_output or "Functional document generation failed."
            tech_text = self.technical_output or "Technical document generation failed."

            # Step 2: Get latest commit SHA
            ref_url = f"{self.GITHUB_API}/repos/{self.GITHUB_USERNAME}/{self.GITHUB_REPO}/git/ref/heads/{self.GITHUB_BRANCH}"
            ref_resp = requests.get(ref_url, headers=self.github_api_headers())
            ref_resp.raise_for_status()
            latest_commit_sha = ref_resp.json()["object"]["sha"]

            # Step 3: Get base tree SHA
            commit_url = f"{self.GITHUB_API}/repos/{self.GITHUB_USERNAME}/{self.GITHUB_REPO}/git/commits/{latest_commit_sha}"
            commit_resp = requests.get(commit_url, headers=self.github_api_headers())
            commit_resp.raise_for_status()
            base_tree_sha = commit_resp.json()["tree"]["sha"]
            if not base_tree_sha:
                return False, "Base tree SHA is missing."

            # Step 4: Create blobs for code files
            blobs = []
            for path, content in self.cleaned.items():
                if path.startswith("/"):
                    path = path.lstrip("/")
                blob_url = f"{self.GITHUB_API}/repos/{self.GITHUB_USERNAME}/{self.GITHUB_REPO}/git/blobs"
                blob_resp = requests.post(
                    blob_url,
                    headers=self.github_api_headers(),
                    json={"content": content, "encoding": "utf-8"},
                )
                blob_resp.raise_for_status()
                blob_sha = blob_resp.json()["sha"]

                blobs.append({
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha,
                })

            # Step 5: Add functional and technical documents as text
            doc_files = {
                "documentation/functional.txt": func_text,
                "documentation/technical.txt": tech_text
            }

            for path, content in doc_files.items():
                blob_url = f"{self.GITHUB_API}/repos/{self.GITHUB_USERNAME}/{self.GITHUB_REPO}/git/blobs"
                blob_resp = requests.post(
                    blob_url,
                    headers=self.github_api_headers(),
                    json={"content": content, "encoding": "utf-8"},
                )
                blob_resp.raise_for_status()
                blob_sha = blob_resp.json()["sha"]

                blobs.append({
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha,
                })

            if not blobs:
                return False, "No files to commit. Blob list is empty."

            # Step 6: Create new tree
            tree_url = f"{self.GITHUB_API}/repos/{self.GITHUB_USERNAME}/{self.GITHUB_REPO}/git/trees"
            tree_payload = {
                "base_tree": base_tree_sha,
                "tree": blobs
            }
            tree_resp = requests.post(tree_url, headers=self.github_api_headers(), json=tree_payload)
            tree_resp.raise_for_status()
            new_tree_sha = tree_resp.json()["sha"]

            # Step 7: Create commit
            new_commit_payload = {
                "message": commit_message,
                "tree": new_tree_sha,
                "parents": [latest_commit_sha]
            }
            commit_url = f"{self.GITHUB_API}/repos/{self.GITHUB_USERNAME}/{self.GITHUB_REPO}/git/commits"
            commit_resp = requests.post(commit_url, headers=self.github_api_headers(), json=new_commit_payload)
            commit_resp.raise_for_status()
            new_commit_sha = commit_resp.json()["sha"]

            # Step 8: Update branch ref
            update_url = f"{self.GITHUB_API}/repos/{self.GITHUB_USERNAME}/{self.GITHUB_REPO}/git/refs/heads/{self.GITHUB_BRANCH}"
            update_resp = requests.patch(update_url, headers=self.github_api_headers(), json={"sha": new_commit_sha})
            update_resp.raise_for_status()

            self.logger.info(f"Code and documentation pushed successfully to: {self.GITHUB_REPO},{self.GITHUB_BRANCH}")
            return True, "Pushed successfully."

        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTPError during git-push: {e.response.status_code} {e.response.reason} - {e.response.text}")
            return False, f"HTTPError: {e.response.status_code} {e.response.reason}"
        except Exception as e:
            self.logger.error(f"Exception during git-push: {str(e)}")
            return False, str(e)

    def run_sdlc(self):
        try:
            self.logger.info("Starting SDLC process.")
            self.pdf_extractor()
            self.functional_document()
            print('Functional document created.')
            time.sleep(60)
            self.technical_document()
            print('Technical document created.')
            time.sleep(60)
            self.generate_pyspark_code()
            print('Spark code created.')
            self.parse_llm_output()
            self.clean_files_dict()
            self.push_to_github()
            print('Push to github completed.')
            self.logger.info("Completed SDLC process.")
        except Exception as e:
            print(e)