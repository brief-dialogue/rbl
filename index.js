
function createReciveMsg(msg, time) {
    const res = `                <div class="d-flex flex-row justify-content-start mb-4">
                <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava5-bg.webp"
                  alt="avatar 1" style="width: 45px; height: 100%;">
                <div>
                  <p class="small p-2 ms-3 mb-1 rounded-3" style="background-color: #f5f6f7;">${msg}</p>
                  <p class="small ms-3 mb-3 rounded-3 text-muted">${time}</p>
                </div>
              </div>`
    return res;
}
function createSendMsg(msg, time) {
    const res = `                <div class="d-flex flex-row justify-content-end">
                <div>
                  <p class="small p-2 me-3 mb-1 text-white rounded-3 bg-info">${msg}
                  </p>
                  <p class="small me-3 mb-3 rounded-3 text-muted d-flex justify-content-end">${time}</p>
                </div>
                <img src="https://mdbcdn.b-cdn.net/img/Photos/new-templates/bootstrap-chat/ava2-bg.webp"
                  alt="avatar 1" style="width: 45px; height: 100%;">
              </div>`;
    return res;
}
let greetings = new Set([
    "Hello",
    "Hi there",
    "Good morning",
    "Good afternoon",
    "Good evening",
    "It’s nice to meet you",
    "It’s a pleasure to meet you",
    "How may I help you"
])

function checkGreet(msg) {
    let chatSection = document.getElementById("card-body");
    if (chatSection.children.length !== 0)
        return;
    if (greetings.has(msg))
        document.getElementById("greeting").innerText = "true";
}

let ws = new WebSocket("ws://localhost:8000/client_chat");
ws.onopen = ()=>{console.log("socket connected  ")}
ws.onmessage = (event)=>{
    recivedData = JSON.parse(event.data) 
    if(!sessionStorage.getItem("uuid")){
        let uuid = recivedData["data"]['uuid'] 
        sessionStorage.setItem("uuid", uuid);
        return;
    }
    if(!recivedData.data.msg)
        return;
    let d = new Date();
    let res_time = `${d.getHours()}:${d.getMinutes()}`;
    let html = document.getElementById("card-body").innerHTML;
    html += createReciveMsg(recivedData.data.msg, res_time);
    document.getElementById("card-body").innerHTML = html;
    // document.getElementById("emotions").innerText = JSON.stringify(recivedData, null, 2)
} 

function send() {
    let d = new Date();
    let send_time = `${d.getHours()}:${d.getMinutes()}`;    
    let html = document.getElementById("card-body").innerHTML;
    let msg = document.getElementById("exampleFormControlInput3").value;
    document.getElementById("exampleFormControlInput3").value = "";
    html += createSendMsg(msg, send_time);
    document.getElementById("card-body").innerHTML = html;
    // if (document.getElementById("greeting").innerText === "false")
    //     checkGreet(msg);
    ws.send(JSON.stringify({ "msg": msg, "isGreeted": false }));
}