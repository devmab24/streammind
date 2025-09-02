let RunSentimentAnalysis = () => {
    const textToAnalyze = document.getElementById("textToAnalyze").value.trim();
    
    // Check if input is empty
    if (textToAnalyze === "") {
        document.getElementById("system_response").innerHTML = 
            '<div class="alert alert-warning">Please enter some text to analyze.</div>';
        return;
    }
    
    // Show loading message
    document.getElementById("system_response").innerHTML = 
        '<div class="alert alert-info">Analyzing emotions...</div>';

    let xhttp = new XMLHttpRequest();
    
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4) {
            if (this.status == 200) {
                try {
                    const response = JSON.parse(this.responseText);
                    
                    if (response.status === "success") {
                        const emotions = response.emotions;
                        
                        // Format the response nicely
                        const formattedResponse = `
                            <div class="alert alert-success">
                                <h5>Emotion Analysis Results:</h5>
                                <ul class="list-unstyled">
                                    <li><strong>Anger:</strong> ${(emotions.anger * 100).toFixed(1)}%</li>
                                    <li><strong>Disgust:</strong> ${(emotions.disgust * 100).toFixed(1)}%</li>
                                    <li><strong>Fear:</strong> ${(emotions.fear * 100).toFixed(1)}%</li>
                                    <li><strong>Joy:</strong> ${(emotions.joy * 100).toFixed(1)}%</li>
                                    <li><strong>Sadness:</strong> ${(emotions.sadness * 100).toFixed(1)}%</li>
                                </ul>
                                <div class="mt-3">
                                    <strong>Dominant Emotion:</strong> 
                                    <span class="badge badge-primary text-capitalize">${emotions.dominant_emotion}</span>
                                </div>
                            </div>
                        `;
                        
                        document.getElementById("system_response").innerHTML = formattedResponse;
                    } else {
                        document.getElementById("system_response").innerHTML = 
                            `<div class="alert alert-danger">${response.error}</div>`;
                    }
                } catch (e) {
                    document.getElementById("system_response").innerHTML = 
                        '<div class="alert alert-danger">Error parsing response. Please try again.</div>';
                }
            } else if (this.status == 400) {
                try {
                    const errorResponse = JSON.parse(this.responseText);
                    document.getElementById("system_response").innerHTML = 
                        `<div class="alert alert-danger">${errorResponse.error}</div>`;
                } catch (e) {
                    document.getElementById("system_response").innerHTML = 
                        '<div class="alert alert-danger">Bad request. Please check your input.</div>';
                }
            } else {
                document.getElementById("system_response").innerHTML = 
                    '<div class="alert alert-danger">Server error. Please try again later.</div>';
            }
        }
    };
    
    // Encode the text properly for URL
    const encodedText = encodeURIComponent(textToAnalyze);
    xhttp.open("GET", `emotionDetector?textToAnalyze=${encodedText}`, true);
    xhttp.send();
}

// let RunSentimentAnalysis = ()=>{
//     textToAnalyze = document.getElementById("textToAnalyze").value;

//     let xhttp = new XMLHttpRequest();
//     xhttp.onreadystatechange = function() {
//         if (this.readyState == 4 && this.status == 200) {
//             document.getElementById("system_response").innerHTML = xhttp.responseText;
//         }
//     };
//     xhttp.open("GET", "emotionDetector?textToAnalyze"+"="+textToAnalyze, true);
//     xhttp.send();
// }
