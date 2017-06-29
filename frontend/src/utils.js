import { BACKEND_HOST } from './conf'

const addYears = (dt, years) => {dt.setFullYear(dt.getFullYear() + years); return dt;}
const yearsAdded = (dt, years) => addYears(new Date(dt), years);

const addMonths = (dt, months) => dt.setMonth(dt.getMonth() + months);
const monthsAdded = (dt, months) => addMonths(new Date(dt), months);

const addDays = (dt, days) => {dt.setDate(dt.getDate() + days); return dt}
const daysAdded = (dt, days) => addDays(new Date(dt), days);

export function getDateDiff(pre, now) {
  pre = new Date(pre);
  const sign = pre < now ? 1 : -1;
  if (sign < 0) {
    [pre, now] = [now, pre];
  }
  let years = now.getFullYear() - pre.getFullYear();
  if (yearsAdded(pre, years) > now) {
    years -= 1;
  }
  addYears(pre, years);
  let months = 1;
  for (; months <= 12; months += 1) {
    if (monthsAdded(pre, months) > now) {
      months -= 1;
      break;
    }
  }
  addMonths(pre, months);
  let days = 1;
  for (; days <= 31; days += 1) {
    if (daysAdded(pre, days) > now) {
      days -= 1;
      break;
    }
  }
  addDays(pre, days);
  let val = (now - pre) / 1000;
  const seconds = val % 60;
  val = Math.floor(val / 60);
  const minutes = val % 60;
  val = Math.floor(val / 60);
  const hours = val;
  return [years, months, days, hours, minutes, seconds];
}

export async function fetchJSON(method, url, data) {
  url = BACKEND_HOST + url;
  data = data || {};

  const headers = new Headers();
  headers.append('Content-Type', 'application/json');
  const options = {
    method: method,
    headers: headers,
    credentials: 'include',
  }

  if (method === 'POST' || method === 'PUT') {
    Object.assign(options, {
      body: JSON.stringify(data)
    });
  } else if ((method === 'GET' && data) || method === 'DELETE') {
    let args = [];
    Object.keys(data).forEach((key) => {
      const value = data[key];
      if (value !== undefined && value !== null) {
        args.push(encodeURIComponent(key)
            + '='
            + encodeURIComponent(data[key]));
      }
    });
    if (args) {
      url += '?' + args.join('&');
      console.log('fetchJSON, GET', url);
    }
  }

  console.log('Client -----> Server | fetchJSON ' + url);
  console.log(options);
  const resp = await fetch(url, options);
  const json = resp.json();
  json.then((json) => {
    console.log('Client <----- Server | fetchJSON ' + url);
    console.log(json);
  });
  return json;
}

export async function getCurrentUser(then) {
  fetchJSON('GET', '/api/me').then(then);
}
