# Script to be run locally to create EC2 alarms for a region

Import-Module .\ec2-shutdown.psm1 -Force
<# To run for all US regions
    $regions = "us-east-1","us-west-1","us-east-2","us-west-2"
    $regions = "us-west-2"
    foreach($region in $regions){
        Set-TaggedEc2Alarms -region $region
    }
#>
#  To run for current credentialed region
$region = aws configure get region

Set-TaggedEc2Alarms -region $region
