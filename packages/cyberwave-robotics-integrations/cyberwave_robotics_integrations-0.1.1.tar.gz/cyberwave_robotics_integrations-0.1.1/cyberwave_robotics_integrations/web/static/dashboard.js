function sendCommand(alias, cmd){
  fetch(`/robot/${alias}/command/${cmd}`, {method: "POST"});
}

async function updateTelemetry(){
  document.querySelectorAll('.robot').forEach(async div => {
    const alias = div.dataset.alias;
    const res = await fetch(`/robot/${alias}/telemetry`);
    if(res.ok){
      const data = await res.json();
      if(data.bat !== undefined){
        div.querySelector('.battery').textContent = data.bat;
      }
    }
  });
}

setInterval(updateTelemetry, 2000);
window.addEventListener('load', updateTelemetry);
