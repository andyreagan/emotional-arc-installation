// begin with some helper functions
// http://stackoverflow.com/a/1026087/3780153
function capitaliseFirstLetter(string)
{
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// this works really well, but it's deadly slow (working max 5 elements)
// and it's coupled to jquery
// http://stackoverflow.com/a/5047712/3780153
String.prototype.width = function(font) {
    var f = font || '12px arial',
    o = $('<div>' + this + '</div>')
	.css({'position': 'absolute', 'float': 'left', 'white-space': 'nowrap', 'visibility': 'hidden', 'font': f})
	.appendTo($('body')),
    w = o.width();
    o.remove();
    return w;
}

// yup
// http://stackoverflow.com/questions/3883342/add-commas-to-a-number-in-jquery
function commaSeparateNumber(val){
    while (/(\d+)(\d{3})/.test(val.toString())){
	val = val.toString().replace(/(\d+)(\d{3})/, '$1'+','+'$2');
    }
    return val;
}

console.log("would use "+book+" as the default here");

var lang = "english";

function clearPlot() {
    d3.select("#booktitle").selectAll("h2").remove();
    d3.select("#chapters03").select(".canvas").remove();
}

var matrixfile;

function initializePlot(metadata) {
    // go display the basic stuff
    var booktitle = d3.select("#booktitle");
    var title = booktitle.append("h2").text(metadata.title+" ");
    var bookauthor = d3.select("#bookauthor");
    var author = booktitle.append("h2").append("small").text("by "+metadata.author);
    var newignore = metadata.ignorewords.split(",");
    hedotools.shifter.ignore(newignore);
    
    loadCsv(metadata);
}

function loadCsv(metadata) {
    var csvLoadsRemaining = 4;
    var bookfile = "static/data/timeseries/"+metadata.book_id+".csv";
    d3.text(bookfile, function (text) {
	var tmpminwin = 10;
	fulltimeseries = text.split(",").map(parseFloat);
	begtimeseries = fulltimeseries.slice(0,tmpminwin/2+1);
	endtimeseries = fulltimeseries.slice(fulltimeseries.length-1-tmpminwin/2,fulltimeseries.length);
	timeseries = fulltimeseries.slice(tmpminwin/2,fulltimeseries.length-tmpminwin/2);
        if (!--csvLoadsRemaining) initializePlotPlot();
    });
    d3.text("static/data/labMT/labMTscores-"+lang+".csv", function (text) {
        var tmp = text.split("\n");
        //console.log(tmp.length);
        //console.log(tmp[tmp.length-1]);
        var lens = tmp.map(parseFloat);
        var len = lens.length - 1;
        while (!lens[len]) {
            //console.log("in while loop");
            lens = lens.slice(0, len);
            len--;
        }
	hedotools.shifter._lens(lens);
        if (!--csvLoadsRemaining) initializePlotPlot();
    });
    d3.text("static/data/labMT/labMTwords-"+lang+".csv", function (text) {
        var tmp = text.split("\n");
        var words = tmp;
        var len = words.length - 1;
        while (!words[len]) {
            //console.log("in while loop");
            words = words.slice(0, len);
            len--;
        }
	hedotools.shifter._words(words);
        if (!--csvLoadsRemaining) initializePlotPlot();
    });
    d3.text("static/data/labMT/labMTwordsEn-"+lang+".csv", function (text) {
        var tmp = text.split("\n");
        var words_en = tmp;
        var len = words_en.length - 1;
        while (!words_en[len]) {
            //console.log("in while loop");
            words_en = words_en.slice(0, len);
            len--;
        }
	hedotools.shifter._words_en(words_en);
        if (!--csvLoadsRemaining) initializePlotPlot();
    });
    // go make the async call for the full data
    // assume it will load in the time it takes the main timeseries to draw
    // and start using it then
    matrixfile = "static/data/full_matrices/"+metadata.book_id+".csv";
};

function initializePlotPlot(lens, words) {
    // initially apply the lens
    var minSize = 10000;
    var dataSize = 1000;
    minWindows = Math.round(minSize / dataSize);
    // console.log(timeseries);
    // drawBookTimeseries(d3.select("#chapters03"),timeseries);
    hedotools.booktimeseries.setFigure(d3.select("#chapters03"));
    hedotools.booktimeseries.setData(fulltimeseries);
    hedotools.booktimeseries.plot();
    // hedotools.booktimeseries.drawAnnotations();
    // selectChapterTop(d3.select("#chapters01"), timeseries.length);
    // selectChapter(d3.select("#chapters02"), timeseries.length);
};

// make the whole thing
// initializePlot();

var allDataRaw;
// console.log(bookref);

var opts = {
    lines: 13, // The number of lines to draw
    length: 5, // The length of each line
    width: 2, // The line thickness
    radius: 3, // The radius of the inner circle
    corners: 1, // Corner roundness (0..1)
    rotate: 0, // The rotation offset
    direction: 1, // 1: clockwise, -1: counterclockwise
    color: '#000', // #rgb or #rrggbb or array of colors
    speed: 1, // Rounds per second
    trail: 60, // Afterglow percentage
    shadow: false, // Whether to render a shadow
    hwaccel: false, // Whether to use hardware acceleration
    className: 'spinner', // The CSS class to assign to the spinner
    zIndex: 2e9, // The z-index (defaults to 2000000000)
    top: '50%', // Top position relative to parent
    left: '50%' // Left position relative to parent
};

var swap = function(fromId, toId){
    var temp = $("#"+toId).html();
    $("#"+toId).empty().html($("#"+fromId).html());
    $("#"+fromId).empty().html(temp);
    document.getElementById(fromId).setAttribute("id",toId)
    document.getElementById(toId).setAttribute("id",fromId)
}

var draw_wordshift = function(refFextent,compFextent,figure) {
    // initialize new values
    var refF = Array(allDataRaw[0].length);
    var compF = Array(allDataRaw[0].length);
    // fill them with 0's
    for (var i = 0; i < allDataRaw[0].length; i++) {
        refF[i] = 0;
        compF[i] = 0;
    }
    // loop over each slice of data
    for (var i = 0; i < allDataRaw[0].length; i++) {
        // grab the shift vectors
	for (var k = refFextent[0]; k < refFextent[1]; k++) {
            refF[i] += parseFloat(allDataRaw[k][i]);
	}
	for (var k = compFextent[0]; k < compFextent[1]; k++) {
            compF[i] += parseFloat(allDataRaw[k][i]);
	}
    }

    console.log(refF);
    console.log(compF);

    hedotools.shifter._refF(refF);
    hedotools.shifter._compF(compF);
    // use the stop words
    hedotools.shifter.stop();
    hedotools.shifter.shifter();
    var happysad = hedotools.shifter._compH() > hedotools.shifter._refH() ? "happier" : "less happy";
    var shifttext = ["Why comparison section is "+happysad+" than reference section:","Reference section's happiness: "+hedotools.shifter._refH().toFixed(2),"Comparison section's happiness: "+hedotools.shifter._compH().toFixed(2)]

    hedotools.shifter.setfigure(d3.select(figure));
    hedotools.shifter.setText([" "," "," "]);
    hedotools.shifter.setWidth(310);
    hedotools.shifter.plot();
};


function requestFullScreen(element) {
    // Supports most browsers and their versions.
    var requestMethod = element.requestFullScreen || element.webkitRequestFullScreen || element.mozRequestFullScreen || element.msRequestFullscreen;

    if (requestMethod) { // Native full screen.
        requestMethod.call(element);
    } else if (typeof window.ActiveXObject !== "undefined") { // Older IE.
        var wscript = new ActiveXObject("WScript.Shell");
        if (wscript !== null) {
            wscript.SendKeys("{F11}");
        }
    }
}

var elem = document.documentElement; // Make the body go full screen.

document.addEventListener("keydown", function(e) {
    if (e.keyCode == 70) {
        requestFullScreen(elem);
    }
}, false);
