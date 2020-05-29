const walk = require('walk')
const path = require('path')
const Shell = require('node-powershell');

exports.notifyPine = function(req, res) {
    let logger = req.log;    
    const ps = new Shell({
        executionPolicy: 'Bypass',
        noProfile: true
    });
     
    let arrFiles = ['./scripts/build_pine.git.ps1', './scripts/build_pine.node.ps1', './scripts/build_pine.deploy.ps1']
    for (const key in arrFiles) {
        if (arrFiles.hasOwnProperty(key)) {
            const file = arrFiles[key];
            ps.addCommand(file);    
            ps.invoke()
                .then(output => {
                    logger.info("Powershell Data: " + output)
                    console.log(output);
                })
                .catch(err => {
                    logger.error("Powershell Errors: " + err)
                    console.log(err);
                });
        }
    }
}

exports.notifyPineAPI = function(req, res) {
    let logger = req.log;    
    const ps = new Shell({
        executionPolicy: 'Bypass',
        noProfile: true
    });
     
    let arrFiles = ['./scripts/build_pine.be.git.ps1', './scripts/build_pine.be.node.ps1', './scripts/build_pine.be.deploy.ps1']
    for (const key in arrFiles) {
        if (arrFiles.hasOwnProperty(key)) {
            const file = arrFiles[key];
            ps.addCommand(file);    
            ps.invoke()
                .then(output => {
                    logger.info("Powershell Data: " + output)
                    console.log(output);
                })
                .catch(err => {
                    logger.error("Powershell Errors: " + err)
                    console.log(err);
                });
        }
    }
}