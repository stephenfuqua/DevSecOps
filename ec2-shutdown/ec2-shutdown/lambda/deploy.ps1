[CmdletBinding()]
param (
    [Parameter()]
    [string]
    $function = "ec2_shutdown",
    [string]
    $awsprofile = "edfi",
    [string]
    $region = "us-east-1",
    $set_time_hour = 19
)
Import-Module AWSLambdaPSCore
Import-Module AWS.Tools.Common
Import-Module AWS.Tools.EventBridge

$id = aws sts get-caller-identity --query "Account" --output text
if (! $region) {
    $region = aws configure get region
}
Publish-AWSPowerShellLambda -ScriptPath ".\$function\$function.ps1" -Name $function -ProfileName $awsprofile -Region $region

$offset = [Math]::Abs((Get-Date -f "%z"))
$time_hour = (get-date "$($set_time_hour):00").AddHours($offset).ToString("%H")

Write-EVBRule -Name "$($function)_daily" -Description "Shutdown all tagged EC2 instances at specified time daily." -ScheduleExpression "cron(0 $time_hour ? * * *)" -ProfileName $awsprofile -Region $region
$target = New-Object -TypeName Amazon.EventBridge.Model.Target
$target.Id = "1"
$target.Arn = "arn:aws:lambda:$($region):$($id):function:$function"
Write-EVBTarget -Rule "$($function)_daily" -Target $target -ProfileName $awsprofile -Region $region
