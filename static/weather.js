(function(){
const ic=c=>c==0?'fa-sun':c<3?'fa-cloud-sun':c<4?'fa-cloud':c<50?'fa-smog':c<70?'fa-cloud-rain':c<80?'fa-snowflake':c<90?'fa-cloud-showers-heavy':'fa-cloud-bolt';
const tx=c=>c==0?'Clear sky':c<3?'Partly cloudy':c<4?'Overcast':c<50?'Foggy':c<70?'Rain':c<80?'Snow':c<90?'Showers':'Thunderstorm';
document.querySelectorAll('[data-wx]').forEach(el=>{
 const d=el.dataset,u='https://api.open-meteo.com/v1/forecast?latitude='+d.lat+'&longitude='+d.lon+'&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto&forecast_days=4';
 fetch(u).then(r=>r.json()).then(j=>{const c=j.current,x=j.daily;
  let days='';for(let i=1;i<4;i++){const n=new Date(x.time[i]).toLocaleDateString('en-IN',{weekday:'short'});
   days+='<div class="day"><div>'+n+'</div><i class="fa-solid '+ic(x.weather_code[i])+'"></i><div>'+Math.round(x.temperature_2m_max[i])+'° / '+Math.round(x.temperature_2m_min[i])+'°</div><div><i class="fa-solid fa-droplet"></i> '+(x.precipitation_probability_max[i]??0)+'%</div></div>';}
  el.innerHTML='<div class="d-flex align-items-center gap-3 mb-2"><i class="fa-solid '+ic(c.weather_code)+' main"></i><div><div class="big">'+Math.round(c.temperature_2m)+'°C</div><div>'+tx(c.weather_code)+'</div></div><div class="ms-auto text-end small"><div><i class="fa-solid fa-location-dot me-1"></i>'+d.place+'</div><div><i class="fa-solid fa-droplet me-1"></i>'+c.relative_humidity_2m+'%</div><div><i class="fa-solid fa-wind me-1"></i>'+Math.round(c.wind_speed_10m)+' km/h</div></div></div><div class="d-flex gap-2">'+days+'</div>';
 }).catch(()=>{el.innerHTML='<i class="fa-solid fa-cloud-sun me-1"></i>Weather is unavailable right now.'});
});})();
