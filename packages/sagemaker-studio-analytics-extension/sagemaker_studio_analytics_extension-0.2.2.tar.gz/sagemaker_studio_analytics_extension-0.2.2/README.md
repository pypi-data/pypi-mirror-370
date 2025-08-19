# SageMaker Studio Analytics Extension

This is a notebook extension provided by AWS SageMaker Studio Team to integrate with analytics resources. Currently, it supports connecting SageMaker Studio Notebook to Spark(EMR) cluster through SparkMagic library.

## Usage
Before you can use the magic command to connect Studio notebook to EMR, please ensure the SageMaker Studio has the connectivity to Spark cluster(livy service). You can refer to [this AWS blog](https://aws.amazon.com/blogs/machine-learning/amazon-sagemaker-studio-notebooks-backed-by-spark-in-amazon-emr/) for how to set up SageMaker Studio and EMR cluster. 
### Register the magic command:
```buildoutcfg
%load_ext sagemaker_studio_analytics_extension.magics
```
### Show help content:
```buildoutcfg
Docstring:
::
This is a notebook extension provided by AWS SageMaker Studio Team to integrate with analytics resources.
Currently, it supports connecting SageMaker Studio Notebook to EMR clusters and EMR Serverless Applications
through the SparkMagic library.

  %sm_analytics [--auth-type AUTH_TYPE] [--application-id APPLICATION_ID]
                    [--cluster-id CLUSTER_ID] [--language LANGUAGE]
                    [--assumable-role-arn ASSUMABLE_ROLE_ARN]
                    [--emr-execution-role-arn EMR_EXECUTION_ROLE_ARN]
                    [--secret SECRET]
                    [--verify-certificate VERIFY_CERTIFICATE]
                    [--override-krb5-conf | --no-override-krb5-conf]
                    [command ...]


Services currently supported: emr, emr-serverless
Please look at usage of %sm_analytics by executing `%sm_analytics <SERVICE_NAME> help`

Example:
%sm_analytics emr help
%sm_analytics emr-serverless help


positional arguments:
  command               Command to execute. The command consists of a service
                        name followed by a ' ' followed by an operation.
                        Supported services are ['emr', 'emr-serverless'] and
                        supported operations are ['connect', 'help']. For
                        example a valid command is 'emr connect'.

options:
  --auth-type AUTH_TYPE
                        The authentication type to be used. Supported
                        authentication types are {'Kerberos', 'Basic_Access',
                        'None'}.
  --application-id APPLICATION_ID
                        The EMR Serverless Application to connect to
  --cluster-id CLUSTER_ID
                        The cluster id to connect to.
  --language LANGUAGE   Language to use. The supported languages for IPython
                        kernel(s) are {'python', 'scala'}. This is a required
                        argument for IPython kernels, but not for magic
                        kernels such as PySpark or SparkScala.
  --assumable-role-arn ASSUMABLE_ROLE_ARN
                        The IAM role to assume when connecting to a cluster in
                        a different AWS account. This argument is not required
                        when connecting to a cluster in the same AWS account.
  --emr-execution-role-arn EMR_EXECUTION_ROLE_ARN
                        The IAM role passed to EMR to set up EMR job security
                        context. This argument is optional and used when IAM
                        Passthrough feature is enabled for EMR.
  --secret SECRET       The AWS Secrets Manager SecretID.
  --verify-certificate VERIFY_CERTIFICATE
                        Determine if SSL certificate should be verified when
                        using HTTPS to connect to EMR. Supported values are
                        ['True', 'False', 'PathToCert']. If a PathToCert is
                        provided, the certificate verification will be done
                        using the certificate in the provided file path. For
                        public CA issued certificates, enable the certificate
                        validation by setting the parameter as true.
                        Alternatively, you can disable the certificate
                        validation by setting the parameter as false.
  --override-krb5-conf, --no-override-krb5-conf
                        This input only works when the cluster is a Kerberos
                        cluster. Supported values are [True, False].If you
                        want to set it as True, simply add --override-
                        krb5-conf to the end of command with no input value.If
                        you want to set it as False, simply add --no-override-
                        krb5-conf to the end of command with no input
                        value.Default value is True. If set to False,
                        SageMaker will not generate and use krb5.conf file
                        provided by user.User should make sure there is
                        existing krb5.conf file at /etc/krb5.conf
```

### Examples
1. Connect Studio notebook using IPython Kernel to EMR cluster protected by Kerberos. 
```buildoutcfg
%sm_analytics emr connect --cluster-id j-1JIIZS02SEVCS --auth-type Kerberos --language python
```

2. Connect Studio notebook using IPython Kernel to HTTP Basic Auth protected EMR cluster and create the Scala based session.  
```buildoutcfg
%sm_analytics emr connect --cluster-id j-1KHIOQZAQUF5P --auth-type Basic_Access  --language scala
```

3. Connect Studio notebook using IPython Kernel to EMR cluster directly without Livy authentication. 
```buildoutcfg
%sm_analytics emr connect --cluster-id j-1KHIOQZAQUF5P --auth-type None  --language python
```

4. Connect Studio notebook using PySpark or Spark(scala) Kernel to HTTP Basic Auth protected EMR cluster. 
```buildoutcfg
%sm_analytics emr connect --cluster-id j-1KHIOQZAQUF5P --auth-type Basic_Access
```

5. Connect Studio notebook using IPython Kernel to EMR Serverless application and create Scala based session
```buildoutcfg
%sm_analytics emr-serverless connect --application-id <APPLICATION_ID> --emr-execution-role-arn 
<EMR_EXECUTION_ROLE_ARN> --language scala
```                   

6. Connect Studio notebook using PySpark or Spark(scala) Kernel to EMR Serverless application
```buildoutcfg
%sm_analytics emr-serverless connect --application-id <APPLICATION_ID> --emr-execution-role-arn <EMR_EXECUTION_ROLE_ARN>
```    

7. Connect Studio notebook using PySpark or Spark(scala) Kernel to EMR Serverless application in another account
```buildoutcfg
 %sm_analytics emr-serverless connect --application-id <APPLICATION_ID> --emr-execution-role-arn 
 <EMR_EXECUTION_ROLE_ARN> --assumable-role-arn <ASSUMABLE_ROLE_ARN>
```

## License

This library is licensed under the Apache 2.0 License. See the LICENSE file.

