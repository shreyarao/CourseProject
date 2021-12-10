function getArticleDetails() {
    // debugger;
    data = {"body" : document.getElementsByClassName('Article')[0].innerText}
    // debugger;
    return data;
}

function fetchResource(input, init) {
    return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({input, init}, messageResponse => {
            const [response, error] = messageResponse;
            if (response === null) {
                reject(error);
            } else {
                const body = response.body ? new Blob([response.body]) : undefined;
                resolve(new Response(body, {
                    status: response.status,
                    statusText: response.statusText,
                }));
            }
        });
    });
}

function addRelevantArticles(details){

    

    // debugger;
    element1 = document.getElementsByClassName('Article')
    // debugger;
    len = details.articles.length
    art = details.articles
    // debugger;

    element = element1[0]
    element.innerText = element.innerText += '\n'
    element.innerText = element.innerText += 'Related Articles\n '

    var list_of_links = ""
    for(var i = 0; i < len; i++){
        link = "<p><a href=\""+art[i].url+"\">"+(art[i].title.replace(/'/g,''))+"</a></p>"
        list_of_links = list_of_links += link
        list_of_links = list_of_links += '\n'
    }
    // debugger;

    const winHtml = `<!DOCTYPE html>
    <html>
        <head>
            <title>Relevant Articles</title>
        </head>
        <body>
            <h1>Relevant Articles</h1>
            ${list_of_links}
        </body>
    </html>`;

    const winUrl = URL.createObjectURL(
        new Blob([winHtml], { type: "text/html" })
    );

    const win = window.open(
        winUrl,
        "win",
        `width=800,height=400,screenX=200,screenY=200`
    );
}
// debugger;
data2 = getArticleDetails()
// debugger;

fetchResource('http://127.0.0.1:5000/get_top_results', {
    method: 'post',
    body: JSON.stringify(data),
    headers: {
        'Content-Type': 'application/json'
    }
})
.then((res) => res.json())
.then(function(res){
    addRelevantArticles(res)
})