
$('#content').on('mouseover', 'x-mspot', function(evt) {
	var word = this.innerHTML;
	var hv = "";
	for(var i = 0; i < word.length; i++) {
		hv = hv + "[" + $.trim(hvMap[word[i]]) + "]";
	}
	var tooltipLeft = this.offsetLeft + "px";
	var tooltipTop = this.offsetTop + this.offsetHeight + 2 + "px";
	//setTimeout(function() {
		$('<div id="mandarinspotspot-tip-hv">' + hv + '</div>').insertAfter('#mandarinspotspot-tip-py');
		document.getElementById('mandarinspot-tip').style.top = tooltipTop;
		document.getElementById('mandarinspot-tip').style.left = tooltipLeft;
	//}, 0);
});