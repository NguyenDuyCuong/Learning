Write-Output "Node build Start.."

$GitPath = "C:\00 PINE\Setup\SimpleCICD\uGit\frontend"
$SourcePath = Join-Path -Path $GitPath -ChildPath "\source"

Push-Location $SourcePath 
npm i -q
ng build --prod 
Pop-Location
