var mqtt = require('mqtt');
var count = 0;
var client = mqtt.connect("mqtt://localhost:18833", {
    clientId: "mqttjs02"
});
console.log("connected: " + client.connected);

client.on("connect", function () {
    console.log("connected  " + client.connected);

})
//handle errors
client.on("error", function (error) {
    console.log("Can't connect" + error);
    process.exit(1)
});
//publish
function publish(topic, msg, options) {
    console.log("publishing", msg);

    if (client.connected == true) {
        client.publish(topic, msg, options);
    }
}


var timer_id = setInterval(function () {
    publish(topic, message, options);
}, 5000);

//notice this is printed even before we connect
console.log("end of script");