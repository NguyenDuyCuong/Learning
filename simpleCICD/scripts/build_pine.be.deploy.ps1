Write-Output "Deploy Start.."

$GitPath = "C:\00 PINE\Setup\SimpleCICD\uGit\backend"
$SourcePath = Join-Path -Path $GitPath -ChildPath "\source"
$DistributePath = Join-Path -Path $SourcePath -ChildPath "\publish\*"
$IISPath = "C:\00 PINE\Publish\DevApi"
$SiteName = "DEVPINEAPI"

Stop-WebSite -Name $SiteName
Copy-Item -Path $DistributePath -Destination $IISPath -Recurse -Force -Exclude ["web.config"]
Start-WebSite -Name $SiteName

Write-Output "Script Done!"