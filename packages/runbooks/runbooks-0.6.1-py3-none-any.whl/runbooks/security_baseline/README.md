# CloudOps Runbooks: Security Baseline Assessment

## 📖 Overview

The **CloudOps Runbooks: Security Baseline Assessment** is a comprehensive tool designed to evaluate the security of AWS environments in accordance with basic security advisories. It provides a structured way to assess your account and workload configurations against **AWS security best practices** and the **AWS Startup Security Baseline (SSB)**. This tool supports **Python (via pip or Docker)** and **AWS Lambda** deployments, offering flexibility for local testing, CI/CD integration, and scalable cloud execution.

By automating **15+ critical AWS account security and workload security checks**, this solution empowers startups, enterprises, and DevOps teams to validate their cloud security posture, generate actionable reports, and align with AWS Well-Architected principles.

In the **Test Report**, we provide numerous techniques for successfully responding to security threats on AWS with minimal resources. This script is appropriate for usage by early-stage businesses that cannot afford to invest much in security. 


## ✨ Features: Core Capabilities

1. **Account and Workload Security Checks**:
   - Validates IAM configurations, S3 bucket policies, VPC security groups, and CloudTrail settings.
2. **Report Generation**:
   - Generates **multi-language HTML reports** (English, Korean, Japanese).
3. **Actionable Insights**:
   - Provides remediation steps for failed checks, mapped to AWS documentation.
4. **Flexible Deployment**:
   - Usable as a Python library (pip), containerized application (Docker), or AWS Lambda function.
5. **Read-Only Permissions**:
   - Ensures compliance with AWS's **least privilege principle** for non-intrusive diagnostics.

---

## 📂 File Structure

This modular structure ensures maintainability and supports seamless integration into pipelines or ad hoc testing.

```plaintext
src/runbooks/
├── security-baseline/
│   ├── checklist/                  # Security check modules
│   │   ├── iam_password_policy.py  # Checks IAM password policy
│   │   ├── bucket_public_access.py # Validates S3 bucket policies
│   │   └── ...                     # More checks for IAM, S3, CloudTrail, etc.
│   ├── lib/                        # Core utilities and constants
│   │   ├── common.py               # Shared helper functions
│   │   ├── enums.py                # Enumerations for reporting
│   │   ├── language.py             # Multi-language support
│   │   └── permission_list.py      # IAM permissions for checks
│   ├── config.json                 # Configurable parameters for checks
│   ├── permission.json             # IAM policy for execution
│   ├── report_generator.py         # HTML report generator
│   ├── run_script.py               # Main execution script
│   └── report_template_en.html    # Report templates
├── utils/
│   └── logger.py                   # Logging utilities
```

---


## 🚀 Deployment and Usage

The tool offers multiple deployment options tailored for different use cases, such as local testing, CI/CD pipelines, and cloud-native executions.

> TBD: [Watch Video Guide](https://youtu.be/)

### **Option 1: Run Locally with Python**

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/nnthanh101/runbooks.git
    ```

2. Prerequisites: $ `task -d ~ install`
    ```
    echo "Verify the development environment: Python Virtual Environment ..."
    task -d ~ check-tools
    task -d ~ check-aws
    echo "Install Dependencies using uv ..."
    task -d ~ install
    ```

2. **Run the Script**:
   ```bash
   python run_script.py --profile PROFILE_NAME --language EN
   ```

---

### **Option 2: Run with Docker**

1. **Build the Docker Image**:
   ```bash
   docker build -t security-baseline-tester .
   ```

2. **Run the Container**:
   ```bash
   docker run --rm -it -v ~/.aws:/root/.aws:ro security-baseline-tester --profile PROFILE_NAME --language EN
   ```

---

### **Option 3: AWS Lambda Deployment**

1. **Prepare the Lambda Function**:
   - Package the `security-baseline` directory into a ZIP file.
   - Ensure dependencies are included by using tools like **pipenv** or **venv**.

2. **Deploy to AWS Lambda**:
   - Create a Lambda function in the AWS Management Console or using AWS CLI.
   - Attach the `permission.json` IAM policy to the function's execution role.

3. **Invoke the Function**:
   - Use AWS CLI or a scheduled event trigger (e.g., CloudWatch Events).

---

## 🛡️ Security Checks Included

The following checks are aligned with the [AWS Startup Security Baseline (SSB)](https://docs.aws.amazon.com/prescriptive-guidance/latest/aws-startup-security-baseline/welcome.html):

1. **Account-Level Security**:
   - Root account MFA enabled
   - No root access keys
   - Alternate contacts configured

2. **IAM Best Practices**:
   - Password policies enforced
   - MFA for IAM users
   - Attached policies preferred over inline policies

3. **Monitoring and Logging**:
   - CloudTrail enabled across all regions
   - GuardDuty activated
   - CloudWatch alarms configured for critical events

4. **S3 Bucket Policies**:
   - Public access block enabled
   - Encryption enforced for bucket objects

5. **VPC and Network Security**:
   - Validates security group configurations
   - Multi-region usage of resources (e.g., EC2 instances, S3 buckets)

---

## 📊 Reports and Insights

- **Format**: HTML reports generated in the `results/` directory.
- **Languages**: Supported in English, Korean, and Japanese.
- **Insights**:
  - Passed, failed, and skipped checks with detailed descriptions.
  - Direct remediation steps with links to AWS documentation.

Sample Report:

| Check ID | Description                 | Result   | Remediation Steps                  |
|----------|-----------------------------|----------|------------------------------------|
| 01       | Root account MFA enabled    | ✅ Pass  | N/A                                |
| 02       | CloudTrail enabled          | ❌ Fail  | [Enable CloudTrail](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-create-and-update-a-trail.html) |
| 03       | S3 bucket public access     | ✅ Pass  | N/A                                |

---

## 📋 Prerequisites

### **IAM Permissions**

Attach the policy defined in `permission.json` to the IAM user or role executing the script. This policy ensures **read-only access**, except for specific actions like `iam:GenerateCredentialReport`.

### **AWS CLI Configuration**
- Set up credentials in the `~/.aws/credentials` file or use AWS CloudShell.

---

## 🔮 Future Enhancements

1. **Multi-Account Scans**:
   - Expand to support AWS Organizations for enterprise-wide checks.
2. **AI Integration**:
   - Leverage machine learning for automated anomaly detection and remediation suggestions.
3. **Visualization Dashboards**:
   - Integrate with AWS QuickSight or Grafana for real-time security monitoring.

---

## 📢 Feedback and Contributions

We value your feedback! Share your ideas or report issues via:
- **GitHub**: [CloudOps Runbooks Repository](https://github.com/nnthanh101/cloudops-runbooks/issues)
- **Email**: [support@nnthanh101.com](mailto:support@nnthanh101.com)

Let’s work together to make cloud security accessible, effective, and scalable for everyone. 🚀

---

### **Create an IAM User with Permissions**

1. **Navigate to IAM in the AWS Console**:
   - Go to the **IAM service** on the AWS Management Console.

2. **Add a New User**:
   - Select **Users** from the navigation pane, then click **Add users**.
   - Enter a username for the new user under **User name**.

3. **Assign Permissions**:
   - Choose **Attach policies directly** on the **Set permissions** page.
   - Click **Create Policy**, then switch to the **JSON** tab and paste the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "SSBUserPermission",
            "Effect": "Allow",
            "Action": [
                "iam:GenerateCredentialReport",
                "s3:GetBucketPublicAccessBlock",
                "iam:GetAccountPasswordPolicy",
                "cloudtrail:GetTrail",
                "ec2:DescribeInstances",
                "guardduty:ListDetectors",
                "cloudtrail:GetTrailStatus",
                "account:GetAlternateContact",
                "ec2:DescribeRegions",
                "s3:ListBucket",
                "iam:ListUserPolicies",
                "support:DescribeTrustedAdvisorChecks",
                "guardduty:GetDetector",
                "cloudtrail:DescribeTrails",
                "s3:GetAccountPublicAccessBlock",
                "s3:ListAllMyBuckets",
                "ec2:DescribeNetworkInterfaces",
                "ec2:DescribeVpcs",
                "iam:ListAttachedUserPolicies",
                "cloudwatch:DescribeAlarms",
                "iam:ListUsers",
                "sts:GetCallerIdentity",
                "iam:GetCredentialReport",
                "ec2:DescribeSubnets"
            ],
            "Resource": "*"
        }
    ]
}
```

4. **Additional Permissions for CloudShell** *(Optional)*:
   - Add the **AWSCloudShellFullAccess** policy if you plan to use AWS CloudShell for assessments.

5. **Complete User Creation**:
   - Attach the policy to the user, then finish user creation by clicking **Next**.

6. **Generate Access Key**:
   - On the user’s **Security credentials** tab, click **Create access key** to generate the key. [Learn more about creating access keys](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html#Using_CreateAccessKey).

7. **Configure AWS CLI**:
   - Set up your AWS credentials by editing the `~/.aws/credentials` file or use AWS CloudShell directly. [AWS CLI configuration guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html).

---

### **Run the Script**

1. **Run the Script**:
   ```bash
   python3 run_script.py
   ```

2. **Use Profile or Language Options** *(Optional)*:
   - If you configured AWS CLI with a specific profile, run:
     ```bash
     python3 run_script.py --profile PROFILE_NAME --language EN
     ```
   - Supported languages: **English (EN)**, **Korean (KR)**, **Japanese (JP)**, **Vietnamese (VN)**.

3. **View Results**:
   - Upon completion, an HTML report will be generated in the `results/` directory.
   - If running on AWS CloudShell, download the report locally. [How to download files from AWS CloudShell](https://docs.aws.amazon.com/cloudshell/latest/userguide/getting-started.html#download-file).

> ![Sample Report](./images/report_sample_en.png)

> ![Sample Report](./images/report_sample_vn.png)

---

## FAQ: Frequently Asked Questions

### **1. How can I test additional security items to enhance AWS account security?**

To test a broader range of security configurations, consider using [AWS Trusted Advisor](https://aws.amazon.com/blogs/aws/aws-trusted-advisor-new-priority-capability/).
This service regularly analyzes your AWS accounts and helps you implement AWS security best practices aligned with the AWS Well-Architected Framework. By managing your security settings through Trusted Advisor, you can systematically improve the security posture of your AWS environment.

---

### **2. Where can I find more information or guidelines to improve AWS security?**

AWS provides the [AWS Well-Architected Tool](https://docs.aws.amazon.com/wellarchitected/latest/userguide/intro.html), a comprehensive cloud service for evaluating and optimizing your architecture.
This tool includes a **Security Pillar**, which outlines detailed best practices for securing your AWS workloads. Use these guidelines to design, assess, and enhance your security strategy effectively.

---

### **3. Can I scan multiple AWS accounts within the same AWS Organization simultaneously?**

No, this script currently supports scanning a **single AWS account** at a time.
To scan additional AWS accounts in the same organization, you must:
- Create a separate IAM user with the required permissions in each account.
- Run the script individually for each account.

**Note**: Organization-level security settings cannot be assessed using this script. Consider AWS services like **AWS Organizations** for managing policies at scale.

---

### **4. Can I use this script without an IAM Access Key?**

Yes, you can run the script without an IAM Access Key by leveraging IAM roles.
Starting from the **01/Aug/2023**, you can configure and use **IAM Roles** instead of access keys.

Follow these steps:
1. Refer to [Overview of using IAM roles](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-role.html#cli-role-overview) to configure a role profile in the AWS CLI.
2. Execute the script with the `--profile` option as shown below:

```bash
python3 run_script.py --profile PROFILE_NAME --language EN
```

This approach enhances security by reducing the dependency on long-term access keys.

---
