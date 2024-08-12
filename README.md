## System Documentation for DHIS2 Tools Web Application

**Developed by:** Blaise Mafende Mario
**Date:** August 2024  
**Version:** 1.0

### 1. **Introduction**

#### 1.1. **Overview**
DHIS2 Tools is a web-based application designed to simplify and enhance the management of DHIS2 implementations. The platform hosts a suite of tools that allow DHIS2 implementers to interact with their DHIS2 instances without requiring advanced software development skills. The first tool in this suite, the **DHIS2 Metadata Extractor**, provides an intuitive interface for extracting essential metadata, such as program attributes, data elements, program indicators, and option sets, directly from DHIS2 instances and exporting them into an Excel format.

#### 1.2. **Problem Statement**
DHIS2 implementers often struggle with the technical complexities involved in managing metadata within their DHIS2 instances. The process of retrieving, organizing, and exporting this metadata is not straightforward, requiring a deep understanding of DHIS2's API and programming skills. This technical barrier can lead to inefficiencies, reduced data quality, and increased time and resource costs.

#### 1.3. **Objective**
The primary objective of the DHIS2 Tools application is to empower DHIS2 implementers by providing a suite of easy-to-use tools that streamline the process of interacting with DHIS2. The initial focus is on simplifying metadata extraction through the DHIS2 Metadata Extractor, with plans to expand the toolset to address other common challenges faced by DHIS2 users.

### 2. **System Architecture**

#### 2.1. **Technology Stack**
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** Flask (Python)
- **Database:** SQLite (for usage statistics)
- **APIs:** DHIS2 Web API
- **Others:** Flask-Mail for email functionality

#### 2.2. **System Components**
- **DHIS2 Metadata Extractor:** Allows users to log in to their DHIS2 instance, select a program, and choose the metadata they wish to extract (attributes, data elements, program indicators, and option sets). The selected metadata is then exported as an Excel file.
- **Statistics Module:** Tracks and displays usage statistics for the tools, including the total number of extractions, the date of the last extraction, and the number of extractions done in the current period.

### 3. **Functionality**

#### 3.1. **User Login**
Users must provide their DHIS2 instance URL, username, and password to access and use the tools.

#### 3.2. **Program Selection**
After logging in, users can select a DHIS2 program from a list retrieved from their DHIS2 instance.

#### 3.3. **Metadata Selection**
Users can choose which types of metadata to extract:
- **Attributes:** Program-related attributes.
- **Data Elements:** Elements associated with specific program stages.
- **Program Indicators:** Indicators defined within the program.
- **Option Sets:** Available option sets within the DHIS2 instance.

#### 3.4. **Metadata Extraction**
The selected metadata is retrieved from the DHIS2 instance and exported to an Excel file with appropriately named sheets for each metadata type.

#### 3.5. **Usage Statistics**
The application logs each metadata extraction event and provides statistical summaries on the tools page.

### 4. **Benefits for DHIS2 Implementers**
- **Accessibility:** The tools are designed for users with minimal technical expertise, enabling them to manage metadata more efficiently.
- **Efficiency:** Automates the process of metadata extraction, reducing the time and effort required to retrieve and manage DHIS2 data.
- **Scalability:** The platform is designed to be expanded with additional tools, providing a comprehensive solution for various DHIS2 management tasks.

### 5. **Future Development**
The DHIS2 Tools platform will be expanded with additional tools to address other common needs of DHIS2 implementers, such as data import, validation, and reporting functionalities.

### 6. **Conclusion**
The DHIS2 Tools web application, starting with the DHIS2 Metadata Extractor, provides a valuable resource for DHIS2 implementers, simplifying their interaction with DHIS2 and improving the efficiency and effectiveness of their work. This platform is positioned to grow into a comprehensive toolkit for all DHIS2-related tasks.
