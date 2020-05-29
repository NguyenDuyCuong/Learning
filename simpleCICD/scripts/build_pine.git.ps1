Write-Output "Script Start.."
Write-Output "Git pull.."

$GitPath = "C:\00 PINE\Setup\SimpleCICD\uGit\frontend"

git -C $GitPath checkout dev 
git -C $GitPath rebase origin/dev -i --root
