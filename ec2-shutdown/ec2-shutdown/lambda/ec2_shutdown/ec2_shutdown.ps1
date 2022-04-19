# PowerShell script file to be executed as a AWS Lambda function. 
# 
# When executing in Lambda the following variables will be predefined.
#   $LambdaInput - A PSObject that contains the Lambda function input data.
#   $LambdaContext - An Amazon.Lambda.Core.ILambdaContext object that contains information about the currently running Lambda environment.
#
# The last item in the PowerShell pipeline will be returned as the result of the Lambda function.
#
# To include PowerShell modules with your Lambda function, like the AWS.Tools.S3 module, add a "#Requires" statement
# indicating the module and version. If using an AWS.Tools.* module the AWS.Tools.Common module is also required.

#Requires -Modules @{ModuleName='AWS.Tools.Common';ModuleVersion='4.1.53'}
#Requires -Modules @{ModuleName='AWS.Tools.EC2';ModuleVersion='4.1.53'}
# Uncomment to send the input event to CloudWatch Logs
# Write-Host (ConvertTo-Json -InputObject $LambdaInput -Compress -Depth 5)
function Get-MaintainedInstances {
    param(
        [Parameter()]
        [string]
        $tag = "maintained-by",
        [string]
        $region
    )

    $instances = (Get-EC2Instance -region $region -Filter @{Name="tag-key";Values="$tag"})
    #$instances = (aws ec2 describe-instances --filters "Name=tag-key,Values=$tag" | ConvertFrom-Json | Select -ExpandProperty Reservations | Select -ExpandProperty Instances)
    return $instances
}

function Stop-MaintainedEc2Instances {
    param (
        $region
    )
    if (! $region) {
        $region = aws configure get region
    }
    $instances = Get-MaintainedInstances -region $region
    if ($instances.Count -gt 0) {
        Write-Host "Found instances $($instances.InstanceId)"
    }else{
        Write-Host "No instances were found in $region"
        return
    }
    
    #$stopped = aws ec2 stop-instances --instance-ids $instances.InstanceId
    foreach($instance in $instances.Instances){
        Write-Host "Stopping $($instance.InstanceId)"
        Stop-EC2Instance $instance.InstanceId
    }
    #return $stopped
}

Stop-MaintainedEc2Instances -region $ENV:AWS_REGION