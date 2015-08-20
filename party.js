var colors = ["red", "orange", "yellow", "green", "blue", "indigo", "purple"];
var colorIndex = 2;
var cycle;

function leftClick(){
	cycleColor(1);
	clearInterval(cycle);
}

function rightClick(){
	cycleColor(-1);
	clearInterval(cycle);
}

function party(){
	clearInterval(cycle)
	cycle = setInterval(function(){ cycleColor(1) }, 100);
}

function cycleColor(offset){
	var theBlock =  document.querySelector(".the-block");
	numOfColors = colors.length;
	colorIndex = (colorIndex + numOfColors + offset) % numOfColors
	theBlock.style.background = colors[colorIndex];
}
