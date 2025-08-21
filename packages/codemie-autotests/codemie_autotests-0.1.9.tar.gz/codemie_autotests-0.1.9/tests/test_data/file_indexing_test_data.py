file_indexing_test_data = [
    (
        "test.csv",
        "CSV File Test",
        """
            The content of the file is:
                        
            1918: 1922, track A: track B
                        
            1918: 1944, track A: track C
                        
            1918: 1991, track A: track D
        """,
    ),
    (
        "test.json",
        "JSON File Test",
        "The content in the context is from a source document titled 'Automation Test' and contains the word 'Test'.json",
    ),
    (
        "test.yaml",
        "YAML File Test",
        """
            The content in the context is a YAML configuration for an automated test scenario involving a file upload request.
            Here's the content detailed:
            file_upload_request:
              method: POST
              url: "https://example.com/upload"
              headers:
                accept: "application/json"
                Content-Type: "multipart/form-data"
              query_parameters:
                name: "example_file"
                description: "Sample file upload"
              form_data:
                files:
                  file_path: "path/to/sample.txt"
                  mime_type: "text/plain"
              expected_response:
                status_code: 200
                body: "Success"
             It includes details such as request headers, query parameters to include the name and description of the file,
              and form data specifying the file's path and MIME type. The expected response for a successful upload is a status code of `200`
               with a response body containing the word "Success".
        """,
    ),
    (
        "test.xml",
        "XML File Test",
        """
            The content in the context is from a source document named `test.xml`. Here is the content of that document:
            <?xml version="1.0" encoding="UTF-8"?>
            <request>
                <method>POST</method>
                <url>https://example.com/api</url>
                <headers>
                    <header name="accept">application/json</header>
                    <header name="Content-Type">application/xml</header>
                </headers>
                <body>
                    <message>Hello, this is a test request.</message>
                </body>
            </request>
        """,
    ),
    (
        "test.pptx",
        "PPTX File Test",
        """
            The content in the context, sourced from a document titled "test.pptx," covers an overview of software testing. Here's a summary of the key points:
            
            ### Introduction to Testing Concepts
            
            #### What is Software Testing?
            Software testing is defined as the process of evaluating and verifying that a software application operates as expected.
            
            #### Types of Software Testing
            - **Unit Testing**
            - **Integration Testing**
            - **System Testing**
            - **Acceptance Testing**
            
            #### Example Test Case
            - **Test Case:** Verify Login Functionality
                - **Steps:**
                    1. Open the login page.
                    2. Enter valid credentials.
                    3. Click login.
                    4. Verify successful login.
            
            #### Conclusion
            The document concludes by emphasizing that software testing is crucial for ensuring applications work as intended, thereby reducing bugs and enhancing quality.pptx
        """,
    ),
    (
        "test.pdf",
        "PDF File Test",
        """
            It contains a simple message stating "This file is for test purpose." 
            followed by some whitespace and a separator line.
        """,
    ),
]

assistant_chat_test_data = [
    (
        "test.pptx",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        """
            The content in the context, sourced from a document titled "test.pptx," covers an overview of software testing. Here's a summary of the key points:

            ### Introduction to Testing Concepts

            #### What is Software Testing?
            Software testing is defined as the process of evaluating and verifying that a software application operates as expected.

            #### Types of Software Testing
            - **Unit Testing**
            - **Integration Testing**
            - **System Testing**
            - **Acceptance Testing**

            #### Example Test Case
            - **Test Case:** Verify Login Functionality
                - **Steps:**
                    1. Open the login page.
                    2. Enter valid credentials.
                    3. Click login.
                    4. Verify successful login.

            #### Conclusion
            The document concludes by emphasizing that software testing is crucial for ensuring applications work as intended, thereby reducing bugs and enhancing quality.pptx
        """,
    ),
    (
        "test.pdf",
        "application/pdf",
        'It contains a simple message stating "This file is for test purpose." followed by some whitespace and a separator line.',
    ),
    (
        "test.csv",
        "text/csv",
        """
            This shows the complete content of 'test.csv'. The file contains 4 rows and 2 columns,
            with numerical values in the first column and track labels in the second column.
        """,
    ),
    (
        "test.vtt",
        "text/vtt",
        """
            The content of the `test.vtt` file is:

            ```
               WEBVTT

               00:00:00.500 --> 00:00:02.000
               The Web is always changing

               00:00:02.500 --> 00:00:04.300
               and the way we access it is changing
            ```
        """,
    ),
]

large_files_test_data = [
    "large-txt.txt",
    "large-pdf.pdf",
    "large-json.json",
    "large-csv.csv",
    "large-xml.xml",
    "large-yaml.yaml",
]

files_with_different_types_test_data = [
    "test.txt",
    "test.vtt",
    "test.csv",
    "test.json",
    "test.yaml",
    "test.xml",
    "test.pdf",
    "test.pptx",
    "test.gif",
    "test.jpeg",
    "test.jpg",
    "test.png",
    "test.docx",
    "test.xlsx",
    "test.ods",
    "test.ini",
]


RESPONSE_FOR_TWO_FILES = """
    We have the following types of data available:

    1. **CSV Data:**
       - Example data from a CSV file:
         ```
         1918: 1922
         track A: track B
    
         1918: 1944
         track A: track C
    
         1918: 1991
         track A: track D
     ```

    2. **Automation Test Data:**
       - Example data from an automation test labeled as:
         ```
         Test
         ```
"""
