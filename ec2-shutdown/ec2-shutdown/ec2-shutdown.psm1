# Module containing functions to aid in setting EC2 alarms.
# Set-Ec2Alarm - set the cpu alarm on a specified instance ID
# Get-MaintainedInstances - return all EC2 instances with the maintained-by tag
# Set-TaggedEc2Alarms - Combine the above 2 commands based on specified region

$region = aws configure get region
function Set-Ec2Alarm {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [string]
        $instanceId,
        [Parameter()]
        [string]
        $alarmName,
        [string]
        $region,
        [int]
        $threshold = 2,
        [int]
        $period_seconds = 3600,
        [int]
        $evaluation_periods = 1
    )

    if (! $region) {
        $region = aws configure get region
    }
    $alarm = aws cloudwatch put-metric-alarm --alarm-name $alarmName `
        --alarm-description "Alarm when CPU drops below 2 percent for 1 hour" `
        --metric-name CPUUtilization `
        --namespace AWS/EC2 `
        --statistic Maximum `
        --period $period_seconds `
        --threshold $threshold `
        --comparison-operator LessThanOrEqualToThreshold  `
        --dimensions "Name=InstanceId,Value=$instanceId" `
        --evaluation-periods $evaluation_periods `
        --alarm-actions "arn:aws:automate:$($region):ec2:stop" `
        --unit Percent
    return $alarm
}


function Get-MaintainedInstances {
    param(
        [Parameter()]
        [string]
        $tag = "maintained-by"
    )

    $instances = (aws ec2 describe-instances --filters "Name=tag-key,Values=$tag" | ConvertFrom-Json | Select -ExpandProperty Reservations | Select -ExpandProperty Instances)
    return $instances
}

function Set-TaggedEc2Alarms {
    param (
        $region
    )
    if (! $region) {
        $region = aws configure get region
    }
    $instances = Get-MaintainedInstances
    if ($instances.Count -gt 0) {
        Write-Host "Found instances $($instances.InstanceId)"
    }else{
        Write-Host "No instances were found in $region"
        return
    }
    

    foreach($instance in $instances){
        $instanceId = $instance.InstanceId
        $alarmName = "Inactivity Alarm - $instanceId"
        Write-Host "Checking for Alarm $alarmName"

        $instanceAlarm = (aws cloudwatch describe-alarms --alarm-names $alarmName | ConvertFrom-Json)
        if ($instanceAlarm.MetricAlarms.Count -eq 0) {
            Write-Host "Creating Alarm $alarmName"
            $alarm = Set-Ec2Alarm -instanceId $instanceId -alarmName $alarmName
            $alarm
        }else {
            Write-Host "$alarmName exists already!"
            $instanceAlarm
        }
        
        
    }
}