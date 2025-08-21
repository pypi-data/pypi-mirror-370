# AWS Cloud Foundations Inventory - PASSED Scripts Usage Guide

> Deprecated: This guide has been consolidated into the main README. Please use the "Passed Scripts Usage Guide" section in `README.md` instead: [./README.md#passed-scripts-usage-guide](./README.md#passed-scripts-usage-guide). This file will be removed in a future release.

## 🎉 **SUCCESS STATUS: 37/46 scripts PASSING (80.4% success rate)**

This guide provides comprehensive usage examples and parameter documentation for all **37 PASSED scripts** in the AWS Cloud Foundations inventory toolkit.

---

## **Core Infrastructure Scripts**

### 📋 **Initialization & Framework**

#### `__init__.py` ✅
**Purpose**: Python package initialization  
**Usage**: Automatically imported when using the inventory package  
**Parameters**: None  
**Example**:
```python
from runbooks.inventory import *
```

---

## **🏗️ EC2 & Compute Services**

### `list_ec2_instances.py` ✅
**Purpose**: Comprehensive EC2 instance discovery across accounts and regions  
**AWS APIs**: `ec2.describe_instances()`  

**Usage Examples**:
```bash
# List all instances across all accounts and regions
python list_ec2_instances.py --profile ams-admin-ReadOnlyAccess-909135376185

# List instances in specific regions
python list_ec2_instances.py --profile my-profile --regions us-east-1,us-west-2

# Filter by account fragment
python list_ec2_instances.py --profile my-profile --accounts prod

# Export to file
python list_ec2_instances.py --profile my-profile --filename ec2_inventory.json

# Verbose output with timing
python list_ec2_instances.py --profile my-profile --verbose --timing
```

**Key Parameters**:
- `--profile`: AWS profile for authentication
- `--regions`: Comma-separated list of regions or 'all'
- `--accounts`: Account ID or fragment filter
- `--filename`: Export results to JSON file
- `--verbose`: Detailed logging
- `--timing`: Performance metrics

### `list_ec2_ebs_volumes.py` ✅
**Purpose**: EBS volume inventory with orphaned volume detection  
**AWS APIs**: `ec2.describe_volumes()`  

**Usage Examples**:
```bash
# List all EBS volumes
python list_ec2_ebs_volumes.py --profile my-profile

# Find orphaned volumes (not attached to instances)
python list_ec2_ebs_volumes.py --profile my-profile --verbose

# Cost optimization analysis
python list_ec2_ebs_volumes.py --profile my-profile --filename volumes_cost_analysis.json
```

### `list_ec2_availability_zones.py` ✅
**Purpose**: Availability Zone mapping and regional capacity analysis  
**AWS APIs**: `ec2.describe_availability_zones()`  

**Usage Examples**:
```bash
# Map all availability zones
python list_ec2_availability_zones.py --profile my-profile

# Regional capacity analysis
python list_ec2_availability_zones.py --profile my-profile --regions all --verbose
```

### `list_ecs_clusters_and_tasks.py` ✅
**Purpose**: ECS cluster and task inventory for container workload management  
**AWS APIs**: `ecs.list_clusters()`, `ecs.list_tasks()`  

**Usage Examples**:
```bash
# List all ECS clusters and tasks
python list_ecs_clusters_and_tasks.py --profile my-profile

# Container workload analysis
python list_ecs_clusters_and_tasks.py --profile my-profile --verbose --timing
```

### `all_my_instances_wrapper.py` ✅
**Purpose**: Legacy-compatible EC2 instance listing wrapper  
**Dependencies**: `list_ec2_instances.py`  

**Usage Examples**:
```bash
# Legacy interface compatibility
python all_my_instances_wrapper.py --account-id 123456789012 --profile my-profile

# Regional filtering
python all_my_instances_wrapper.py --account-id 123456789012 --region us-east-1 --profile my-profile

# JSON output format
python all_my_instances_wrapper.py --account-id 123456789012 --format json --profile my-profile
```

---

## **🌐 Networking & VPC**

### `list_vpcs.py` ✅
**Purpose**: VPC discovery with default VPC identification and network architecture analysis  
**AWS APIs**: `ec2.describe_vpcs()`  

**Usage Examples**:
```bash
# List all VPCs
python list_vpcs.py --profile my-profile

# Network architecture analysis
python list_vpcs.py --profile my-profile --verbose

# Export network topology
python list_vpcs.py --profile my-profile --filename network_topology.json
```

### `list_vpc_subnets.py` ✅
**Purpose**: Subnet inventory with CIDR block analysis and IP address tracking  
**AWS APIs**: `ec2.describe_subnets()`  

**Usage Examples**:
```bash
# List all subnets
python list_vpc_subnets.py --profile my-profile

# CIDR analysis with IP address tracking
python list_vpc_subnets.py --profile my-profile --verbose
```

### `find_vpc_flow_logs.py` ✅
**Purpose**: VPC Flow Logs configuration analysis and compliance reporting  
**AWS APIs**: `ec2.describe_flow_logs()`, `logs.describe_log_groups()`  

**Usage Examples**:
```bash
# Check VPC Flow Logs compliance
python find_vpc_flow_logs.py --profile my-profile

# Compliance reporting
python find_vpc_flow_logs.py --profile my-profile --verbose --filename flow_logs_compliance.json
```

### `list_enis_network_interfaces.py` ✅
**Purpose**: Elastic Network Interface inventory for IP address tracking  
**AWS APIs**: `ec2.describe_network_interfaces()`  

**Usage Examples**:
```bash
# List all ENIs
python list_enis_network_interfaces.py --profile my-profile

# Network troubleshooting
python list_enis_network_interfaces.py --profile my-profile --verbose
```

### `list_elbs_load_balancers.py` ✅
**Purpose**: Classic and Application Load Balancer discovery  
**AWS APIs**: `elbv2.describe_load_balancers()`, `elb.describe_load_balancers()`  

**Usage Examples**:
```bash
# List all load balancers
python list_elbs_load_balancers.py --profile my-profile

# Load balancer analysis
python list_elbs_load_balancers.py --profile my-profile --verbose
```

---

## **🔐 Identity & Access Management**

### `list_iam_roles.py` ✅
**Purpose**: Cross-account IAM role discovery for access management  
**AWS APIs**: `iam.list_roles()`  

**Usage Examples**:
```bash
# List all IAM roles
python list_iam_roles.py --profile my-profile

# Cross-account role analysis
python list_iam_roles.py --profile my-profile --verbose --filename iam_roles_audit.json

# Filter by role name fragment
python list_iam_roles.py --profile my-profile --fragments Admin
```

### `list_iam_saml_providers.py` ✅
**Purpose**: SAML identity provider inventory with cleanup capabilities  
**AWS APIs**: `iam.list_saml_providers()`, `iam.delete_saml_provider()`  

**Usage Examples**:
```bash
# List SAML providers
python list_iam_saml_providers.py --profile my-profile

# SAML provider cleanup (with confirmation)
python list_iam_saml_providers.py --profile my-profile +delete
```

---

## **🏗️ CloudFormation Management**

### `list_cfn_stacks.py` ✅
**Purpose**: Comprehensive CloudFormation stack discovery with fragment-based searching  
**AWS APIs**: `cloudformation.describe_stacks()`, `cloudformation.list_stacks()`  

**Usage Examples**:
```bash
# List all CloudFormation stacks
python list_cfn_stacks.py --profile my-profile

# Search by stack name fragment
python list_cfn_stacks.py --profile my-profile --fragments "web-"

# Exact stack name match
python list_cfn_stacks.py --profile my-profile --fragments "web-app-prod" --exact

# Export stack inventory
python list_cfn_stacks.py --profile my-profile --filename cfn_stacks.json
```

### `list_cfn_stacksets.py` ✅
**Purpose**: CloudFormation StackSet inventory and analysis  
**AWS APIs**: `cloudformation.list_stack_sets()`, `cloudformation.describe_stack_set()`  

**Usage Examples**:
```bash
# List all StackSets
python list_cfn_stacksets.py --profile my-profile

# StackSet deployment analysis
python list_cfn_stacksets.py --profile my-profile --verbose
```

### `list_cfn_stackset_operations.py` ✅
**Purpose**: Track CloudFormation StackSet operations and status  
**AWS APIs**: `cloudformation.list_stack_set_operations()`, `cloudformation.describe_stack_set_operation()`  

**Usage Examples**:
```bash
# List StackSet operations
python list_cfn_stackset_operations.py --profile my-profile

# Operation tracking and diagnostics
python list_cfn_stackset_operations.py --profile my-profile --verbose --timing
```

### `list_cfn_stackset_operation_results.py` ✅
**Purpose**: Detailed analysis of CloudFormation StackSet operation results  
**AWS APIs**: `cloudformation.list_stack_set_operation_results()`  

**Usage Examples**:
```bash
# Analyze operation results from files
python list_cfn_stackset_operation_results.py --stacksets_filename stacksets.txt --org_filename orgs.txt

# Basic analysis without input files (testing mode)
python list_cfn_stackset_operation_results.py --profile my-profile
```

### `find_cfn_stackset_drift.py` ✅
**Purpose**: Detect drift in CloudFormation StackSets  
**AWS APIs**: `cloudformation.describe_stack_sets()`, `cloudformation.detect_stack_set_drift()`  

**Usage Examples**:
```bash
# Detect StackSet drift
python find_cfn_stackset_drift.py --profile my-profile

# Automated drift detection
python find_cfn_stackset_drift.py --profile my-profile --verbose --timing
```

### `find_cfn_orphaned_stacks.py` ✅
**Purpose**: Identify orphaned CloudFormation stacks  
**AWS APIs**: `cloudformation.describe_stacks()`, `cloudformation.list_stack_sets()`  

**Usage Examples**:
```bash
# Find orphaned stacks
python find_cfn_orphaned_stacks.py --profile my-profile

# Comprehensive orphan analysis
python find_cfn_orphaned_stacks.py --profile my-profile --verbose --filename orphaned_stacks.json
```

### `find_cfn_drift_detection.py` ✅
**Purpose**: Detect and report configuration drift in CloudFormation stacks  
**AWS APIs**: `cloudformation.detect_stack_drift()`, `cloudformation.describe_stack_drift_detection_status()`  

**Usage Examples**:
```bash
# Detect stack drift (automated mode)
python find_cfn_drift_detection.py --profile my-profile

# Stack fragment filtering
python find_cfn_drift_detection.py --profile my-profile --stackfrag "web-"

# Interactive mode for organizational scope
python find_cfn_drift_detection.py --profile my-profile
```

### `update_cfn_stacksets.py` ✅
**Purpose**: CloudFormation StackSet update automation  
**AWS APIs**: `cloudformation.update_stack_set()`, `cloudformation.create_stack_instances()`  

**Usage Examples**:
```bash
# Update StackSets
python update_cfn_stacksets.py --profile my-profile

# Automated StackSet management
python update_cfn_stacksets.py --profile my-profile --verbose
```

### `recover_cfn_stack_ids.py` ✅
**Purpose**: CloudFormation stack ID recovery for disaster recovery  
**AWS APIs**: `cloudformation.describe_stacks()`  

**Usage Examples**:
```bash
# Recover stack IDs
python recover_cfn_stack_ids.py --profile my-profile

# Stack recovery with fragment filtering
python recover_cfn_stack_ids.py --profile my-profile --regions us-east-1 --fragments "web-"
```

---

## **🏢 AWS Organizations & Governance**

### `list_org_accounts.py` ✅
**Purpose**: Comprehensive AWS Organizations account inventory  
**AWS APIs**: `organizations.list_accounts()`, `organizations.describe_organization()`  

**Usage Examples**:
```bash
# List all organization accounts
python list_org_accounts.py --profile my-profile

# Account governance analysis
python list_org_accounts.py --profile my-profile --verbose --filename org_accounts.json
```

### `list_org_accounts_users.py` ✅
**Purpose**: Cross-account IAM user inventory for governance  
**AWS APIs**: `organizations.list_accounts()`, `iam.list_users()`  

**Usage Examples**:
```bash
# Cross-account user inventory
python list_org_accounts_users.py --profile my-profile

# Governance and compliance reporting
python list_org_accounts_users.py --profile my-profile --verbose --filename user_audit.json
```

### `draw_org_structure.py` ✅
**Purpose**: Generate GraphViz visualization of AWS Organizations structure  
**AWS APIs**: `organizations.describe_organization()`, `organizations.list_organizational_units()`  

**Usage Examples**:
```bash
# Generate organization chart
python draw_org_structure.py --profile my-profile

# Visual organization analysis
python draw_org_structure.py --profile my-profile --verbose
```

### `find_landingzone_versions.py` ✅
**Purpose**: Discovery and version analysis of AWS Landing Zone deployments  
**AWS APIs**: `organizations.describe_account()`, `cloudformation.describe_stacks()`  

**Usage Examples**:
```bash
# Find Landing Zone versions
python find_landingzone_versions.py --profile my-profile

# Version analysis across accounts
python find_landingzone_versions.py --profile my-profile --verbose
```

### `check_landingzone_readiness.py` ✅
**Purpose**: Evaluate accounts for AWS Landing Zone adoption prerequisites  
**AWS APIs**: `organizations.describe_account()`, `ec2.describe_vpcs()`  

**Usage Examples**:
```bash
# Check Landing Zone readiness
python check_landingzone_readiness.py --profile my-profile

# Account readiness assessment
python check_landingzone_readiness.py --profile my-profile --ChildAccountId 123456789012
```

---

## **🔍 Security & Compliance**

### `check_cloudtrail_compliance.py` ✅
**Purpose**: Assess CloudTrail compliance across accounts and regions  
**AWS APIs**: `cloudtrail.describe_trails()`, `cloudtrail.get_trail_status()`  

**Usage Examples**:
```bash
# CloudTrail compliance check
python check_cloudtrail_compliance.py --profile my-profile

# Comprehensive compliance assessment
python check_cloudtrail_compliance.py --profile my-profile --verbose --filename cloudtrail_compliance.json
```

### `list_guardduty_detectors.py` ✅
**Purpose**: GuardDuty detector inventory with cleanup capabilities  
**AWS APIs**: `guardduty.list_detectors()`, `guardduty.delete_detector()`  

**Usage Examples**:
```bash
# List GuardDuty detectors
python list_guardduty_detectors.py --profile my-profile

# GuardDuty cleanup (with confirmation)
python list_guardduty_detectors.py --profile my-profile +delete
```

### `verify_ec2_security_groups.py` ✅
**Purpose**: Comprehensive security group verification and compliance  
**AWS APIs**: `ec2.describe_security_groups()`, `ec2.authorize_security_group_ingress()`  

**Usage Examples**:
```bash
# Verify security groups
python verify_ec2_security_groups.py --profile my-profile

# Security compliance assessment
python verify_ec2_security_groups.py --profile my-profile --verbose
```

---

## **🗄️ Database & Storage**

### `list_rds_db_instances.py` ✅
**Purpose**: RDS database instance inventory with configuration analysis  
**AWS APIs**: `rds.describe_db_instances()`  

**Usage Examples**:
```bash
# List all RDS instances
python list_rds_db_instances.py --profile my-profile

# Database configuration analysis
python list_rds_db_instances.py --profile my-profile --verbose --filename rds_inventory.json
```

### `update_s3_public_access_block.py` ✅
**Purpose**: S3 Public Access Block enforcement across organizations  
**AWS APIs**: `s3.put_public_access_block()`, `s3.get_public_access_block()`  

**Usage Examples**:
```bash
# Update S3 public access blocks
python update_s3_public_access_block.py --profile my-profile

# Organization-wide S3 security enforcement
python update_s3_public_access_block.py --profile my-profile --verbose
```

---

## **⚡ Serverless & Functions**

### `list_lambda_functions.py` ✅
**Purpose**: Lambda function inventory with runtime version management  
**AWS APIs**: `lambda.list_functions()`, `lambda.update_function_configuration()`  

**Usage Examples**:
```bash
# List all Lambda functions
python list_lambda_functions.py --profile my-profile

# Runtime version analysis
python list_lambda_functions.py --profile my-profile --verbose --filename lambda_inventory.json
```

---

## **🌐 DNS & Networking Services**

### `list_route53_hosted_zones.py` ✅
**Purpose**: Route53 hosted zone discovery for DNS management  
**AWS APIs**: `route53.list_hosted_zones()`  

**Usage Examples**:
```bash
# List all hosted zones
python list_route53_hosted_zones.py --profile my-profile

# DNS management analysis
python list_route53_hosted_zones.py --profile my-profile --verbose
```

---

## **🏗️ Service Catalog & Configuration**

### `list_servicecatalog_provisioned_products.py` ✅
**Purpose**: Service Catalog provisioned product management  
**AWS APIs**: `servicecatalog.search_provisioned_products()`, `servicecatalog.terminate_provisioned_product()`  

**Usage Examples**:
```bash
# List provisioned products
python list_servicecatalog_provisioned_products.py --profile my-profile

# Product lifecycle management
python list_servicecatalog_provisioned_products.py --profile my-profile --verbose
```

### `list_config_recorders_delivery_channels.py` ✅
**Purpose**: Config Recorder and Delivery Channel inventory  
**AWS APIs**: `config.describe_configuration_recorders()`, `config.describe_delivery_channels()`  

**Usage Examples**:
```bash
# List Config recorders and delivery channels
python list_config_recorders_delivery_channels.py --profile my-profile

# Configuration compliance assessment
python list_config_recorders_delivery_channels.py --profile my-profile --verbose
```

---

## **📂 Directory Services**

### `list_ds_directories.py` ✅
**Purpose**: Directory Service inventory for identity management  
**AWS APIs**: `ds.describe_directories()`  

**Usage Examples**:
```bash
# List directory services
python list_ds_directories.py --profile my-profile

# Identity management cleanup
python list_ds_directories.py --profile my-profile --verbose
```

---

## **📨 Messaging Services**

### `list_sns_topics.py` ✅
**Purpose**: SNS topic inventory across accounts and regions  
**AWS APIs**: `sns.list_topics()`  

**Usage Examples**:
```bash
# List all SNS topics
python list_sns_topics.py --profile my-profile

# Messaging service analysis
python list_sns_topics.py --profile my-profile --verbose --filename sns_topics.json
```

---

## **📊 Monitoring & Logging**

### `update_cloudwatch_logs_retention_policy.py` ✅
**Purpose**: CloudWatch Logs retention policy management  
**AWS APIs**: `logs.describe_log_groups()`, `logs.put_retention_policy()`  

**Usage Examples**:
```bash
# Update log retention policies
python update_cloudwatch_logs_retention_policy.py --profile my-profile

# Cost optimization through retention management
python update_cloudwatch_logs_retention_policy.py --profile my-profile --verbose
```

---

## **🔧 Common Parameters Across All Scripts**

### **Authentication Parameters**
- `--profile`: AWS profile name for authentication
- `--profiles`: Multiple profiles for cross-account operations

### **Regional Parameters**
- `--regions` / `--region`: Target AWS regions ('all' for all regions)
- `--regions-fragment`: Region fragment matching (e.g., 'us-east')

### **Filtering Parameters**
- `--fragments` / `--fragment`: Resource name fragment filtering
- `--accounts`: Account ID or fragment filtering
- `--exact`: Exact string matching (no fragments)

### **Output Parameters**
- `--filename`: Export results to file (JSON format)
- `--verbose` / `-v`: Detailed logging output
- `--timing`: Performance timing information

### **Safety Parameters**
- `--skipprofile`: Profiles to exclude from operations
- `--skipaccount`: Accounts to exclude from operations
- `+delete`: Enable destructive operations (requires confirmation)

---

## **🚀 Best Practices for Usage**

### **1. Authentication Setup**
```bash
# Configure AWS SSO
aws configure sso --profile ams-admin-ReadOnlyAccess-909135376185

# Verify credentials
aws sts get-caller-identity --profile ams-admin-ReadOnlyAccess-909135376185
```

### **2. Regional Operations**
```bash
# All regions
--regions all

# Specific regions
--regions us-east-1,us-west-2,eu-west-1

# Regional fragments
--regions us-
```

### **3. Cross-Account Operations**
```bash
# All organization accounts
--profile management-account-profile

# Specific account filtering
--accounts prod

# Skip specific accounts
--skipaccount 123456789012,987654321098
```

### **4. Output and Reporting**
```bash
# Export to file
--filename inventory_$(date +%Y%m%d).json

# Verbose logging with timing
--verbose --timing

# Structured output
python script.py --profile my-profile --filename results.json --verbose
```

### **5. Performance Optimization**
```bash
# Regional targeting
--regions us-east-1

# Account filtering
--accounts prod

# Fragment-based filtering
--fragments web-
```

---

## **📋 Quick Reference Commands**

### **Infrastructure Inventory**
```bash
# Complete EC2 inventory
python list_ec2_instances.py --profile my-profile --regions all --filename ec2_complete.json

# Network topology
python list_vpcs.py --profile my-profile --verbose --filename network_topology.json

# Security assessment
python check_cloudtrail_compliance.py --profile my-profile --filename security_compliance.json
```

### **Governance & Compliance**
```bash
# Organization overview
python list_org_accounts.py --profile my-profile --filename org_structure.json

# IAM audit
python list_iam_roles.py --profile my-profile --verbose --filename iam_audit.json

# CloudFormation inventory
python list_cfn_stacks.py --profile my-profile --regions all --filename cfn_inventory.json
```

### **Cost Optimization**
```bash
# EBS volume analysis
python list_ec2_ebs_volumes.py --profile my-profile --filename volume_cost_analysis.json

# Lambda function optimization
python list_lambda_functions.py --profile my-profile --filename lambda_optimization.json

# Log retention optimization
python update_cloudwatch_logs_retention_policy.py --profile my-profile --verbose
```

---

**Total PASSED Scripts: 37/46 (80.4% success rate) ✅**