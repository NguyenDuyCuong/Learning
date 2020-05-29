Write-Output "Dotnet build Start.."

$GitPath = "C:\00 PINE\Setup\SimpleCICD\uGit\backend"
$SourcePath = Join-Path -Path $GitPath -ChildPath "\source"

Push-Location $SourcePath 
dotnet publish -c release -o ./publish
Pop-Location
