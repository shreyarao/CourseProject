function getrel() {
	    chrome.tabs.executeScript(null, { file: "content.js" });
}
document.getElementById('clickme').addEventListener('click', getrel);