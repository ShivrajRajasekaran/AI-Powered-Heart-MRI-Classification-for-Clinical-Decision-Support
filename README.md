# AI-Powered-Heart-MRI-Classification-for-Clinical-Decision-Support

*A project for the IBM Datathon 2025 by Team BIG IRON.*

This project is an enterprise-grade, full-stack web application designed to assist medical professionals by providing instant, AI-powered classification of heart MRI scans. It acts as an intelligent "clinical co-pilot," integrating a deep learning model with a suite of IBM Cloud services to deliver a secure, scalable, and trustworthy diagnostic support tool.

---

## The Problem:

The manual analysis of cardiac MRI scans is a critical but challenging task in modern healthcare. The process is:
* *Time-Consuming:* Requiring significant effort from highly specialized radiologists, creating diagnostic bottlenecks.
* *Subjective:* Visual interpretation can vary between experts, potentially affecting diagnostic consistency.
* *Reactive:* Clinicians lack automated tools to help them prioritize urgent cases or see trends in their diagnostic data.

## Our Solution

We have built a complete, end-to-end system that addresses these challenges by integrating multiple layers of AI and cloud technology. Our solution provides:
* *Automated Classification:* A web portal where a technician can upload an MRI and receive an instant diagnosis ("Sick" or "Normal") from our custom-trained AI model.
* *Trustworthy AI:* We go beyond a simple diagnosis by providing "Explainable AI" to build clinical trust.
* *Proactive Insights:* The system automatically flags high-priority cases, transforming it from a simple tool into an intelligent co-pilot.

---

## Live Demo & Workflow

Here is the end-to-end workflow of our application in action:

1.  *Login & Proactive Alerts:* An admin user logs into the secure web portal. The main dashboard immediately displays *"Actionable Insights"*, alerting the user to any recent, high-priority "Sick" diagnoses from the last 24 hours (Upgrade 2).
2.  *Patient Validation:* The user enters a Patient ID, which is validated in real-time against our *IBM Db2 on Cloud* database.
3.  *AI Analysis & XAI:* The user uploads an MRI.
    * The *AI model (CNN)* runs a prediction.
    * The original MRI is securely uploaded to *IBM Cloud Object Storage*.
    * If the diagnosis is "Sick," an *Explainable AI (XAI) heatmap* is generated and also uploaded to Cloud Storage (Upgrade 1).
4.  *Database Update:* The patient's record in *IBM Db2* is updated with the diagnosis, confidence score, and the secure URL to the MRI in Cloud Storage.
5.  *Results Display:* The user is shown a results page with the diagnosis, the original MRI, and the XAI heatmap displayed side-by-side.
6.  *Conversational AI:* The user can interact with the integrated *IBM Watsonx Assistant* to ask complex questions of the live database, such as "How many patients are diagnosed as 'Sick'?" or "Summarize the report for patient P-12345."

<img width="1143" height="785" alt="Screenshot 2025-10-11 094258" src="https://github.com/user-attachments/assets/f2e641cb-ccc1-4aca-a9a8-4f25d9aecd21" />

<img width="1807" height="810" alt="Screenshot 2025-10-11 095100" src="https://github.com/user-attachments/assets/4541518f-75af-421f-a0f3-cd2ae051c2b3" />

<img width="1919" height="975" alt="Screenshot 2025-10-15 131503" src="https://github.com/user-attachments/assets/f164dc9a-12ad-404a-89fe-134522086734" />

<img width="1917" height="962" alt="Screenshot 2025-10-15 131608" src="https://github.com/user-attachments/assets/3ea96283-168d-4851-9437-594c7d21b774" />

<img width="1418" height="717" alt="Screenshot 2025-10-03 223856" src="https://github.com/user-attachments/assets/27d294a9-4b1d-4ee2-9cb0-5041379015c3" />

*Here is the youtube link:*
https://youtu.be/JMZrROrt5qQ?si=V046ShjApX__89Iv
---

## Key Features

* *Explainable AI (XAI) Heatmaps:* For every "Sick" diagnosis, the system generates a Grad-CAM heatmap to visually show why the AI made its decision, building clinical trust.
* *Proactive "AI Clinical Analyst":* The main dashboard proactively flags recent, high-priority cases from the database, helping to manage clinical workload.
* *Data-Driven Conversational AI:* An IBM Watsonx Assistant is integrated as a digital co-pilot that can perform live queries against the IBM Db2 database.
* *Secure IBM Cloud Architecture:* A professional, enterprise-grade foundation using IBM Db2 for patient records and IBM Cloud Object Storage for sensitive MRI images.
* *Full Web Application:* A complete user portal with secure login, file upload, detailed results pages, and a printable report generator.

---

## Technology Stack

| Category              | Technology / Service                                      |
| --------------------- | --------------------------------------------------------- |
| *AI / Deep Learning* | TensorFlow, Keras, tf-explain (for XAI)                 |
| *Backend* | Python, Flask                                             |
| *Database* | IBM Db2 on Cloud                                          |
| *File Storage* | IBM Cloud Object Storage                                  |
| *Conversational AI* | IBM Watsonx Assistant                                     |
| *Frontend* | HTML, CSS, JavaScript                                     |
| *Deployment / Demo* | ngrok                                                   |

---

## Project Setup

To run this project locally, follow these steps:

*1. Prerequisites:*
* Python 3.9+
* An IBM Cloud account with provisioned instances of:
    * IBM Db2 on Cloud
    * IBM Cloud Object Storage
    * IBM Watsonx Assistant

*2. Clone the Repository:*
```bash
git clone <your-repo-url>
cd <your-repo-folder>
