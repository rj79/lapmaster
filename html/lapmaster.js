"use strict";
if (typeof LM === 'undefined') {
    var LM = {};
    LM.poll_interval = 500;
    LM.clock_interval = 1000;
    LM.stamp = null;
}

LM.init = function()
{
    LM.stamp = document.getElementById("versionstamp").getAttribute("versionstamp")
    LM.update_clock();
    setTimeout(LM.check_stamp, LM.poll_interval);
    setTimeout(LM.update_clock, LM.clock_interval);
};

LM.check_stamp = function() {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/versionstamp", false);
    xhr.send();
    var stamp = xhr.responseText;
    if (stamp != LM.stamp) {
        LM.stamp = stamp;
        location.reload();
    }
    else {
        setTimeout(LM.check_stamp, LM.poll_interval);
    }
};

LM.leading_zero = function(n)
{
    if (n < 10) {
	return "0" + n.toString();
    }
    else {
	return n.toString();
    }
};

LM.update_clock = function()
{
    var date = new Date();
    var h = LM.leading_zero(date.getHours());
    var m = LM.leading_zero(date.getMinutes());
    var s = LM.leading_zero(date.getSeconds());
    document.getElementById('clock').innerHTML = h + ":" + m + ":" + s;
    setTimeout(LM.update_clock, LM.clock_interval);
};
