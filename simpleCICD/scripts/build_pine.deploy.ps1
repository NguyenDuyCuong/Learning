Write-Output "Deploy Start.."

$GitPath = "C:\00 PINE\Setup\SimpleCICD\uGit\frontend"
$SourcePath = Join-Path -Path $GitPath -ChildPath "\source"
$DistributePath = Join-Path -Path $SourcePath -ChildPath "\dist\app\*"
$IISPath = "C:\00 PINE\Publish\DevWeb"
$SiteName = "DEVPINE"

Stop-WebSite -Name $SiteName
Copy-Item -Path $DistributePath -Destination $IISPath -Recurse -Force -Exclude ["web.config"]
Start-WebSite -Name $SiteName

Write-Output "Script Done!"