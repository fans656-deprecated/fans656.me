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

export async function fetchData(method, url, data, success, error) {
  if (data instanceof Function) {
    error = success;
    success = data;
    data = undefined;
  }
  const externalURL = url.startsWith('http');
  let options;
  [url, options] = prepareFetch(method, url, data);

  console.log(method + ' ' + url);
  if (method === 'POST' || method === 'PUT') {
    console.log(options);
  }
  const resp = await fetch(url, options);
  const text = resp.text();
  if (externalURL) {
    text.then(success);
  }
  text.then(text => {
    try {
      const json = JSON.parse(text);
      console.log('\n');
      console.log('=== RESPONSE ==================================');
      console.log(method + ' ' + url);
      console.log(json);
      if (json.errno) {
        console.log('[RESPONSE with nonzero errno]');
        if (error) {
          error(json);
        }
      } else if (success) {
        success(json);
      }
      console.log('=== RESPONSE END ==============================');
      console.log('\n');
    } catch (e) {
      console.log('\n');
      console.log('[ERROR] ' + method + ' ' + url);
      console.log(e);
      console.log('================ Body ================');
      console.log(text);
      console.log('============ End of body =============');
      console.log('[ERROR end]');
      console.log('\n');
    }
  }).catch(e => {
    console.log('\n');
    console.log('[ERROR] ' + method + ' ' + url);
    console.log(e);
    console.log('[ERROR end]');
    console.log('\n');
  });
}

export async function fetchJSON(method, url, data) {
  let options;
  [url, options] = prepareFetch(method, url, data);

  console.log('-----> ' + method + ' ' + url);
  if (method === 'POST' || method === 'PUT') {
    console.log(options);
  }
  const resp = await fetch(url, options);
  const json = resp.json();
  json.then((json) => {
    console.log('\n');
    console.log('=== RESPONSE ==================================');
    console.log(method + ' ' + url);
    console.log(json);
    console.log('=== RESPONSE END ==============================');
    console.log('\n');
  });
  if (json.errno) {
    alert(json.detail);
    console.log(json.detail);
    throw Error(json);
  }
  return json;
}

function prepareFetch(method, url, data) {
  if (!url.startsWith('http')) {
    url = BACKEND_HOST + url;
  }
  data = data || {};

  const headers = new Headers();
  headers.append('Content-Type', 'application/json');
  headers.append('Accept', 'application/json');
  if (BACKEND_HOST.slice(5) !== 'https') {
    headers.append('Cache-Control', 'no-cache');
  }
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
      let value = data[key];
      if (value !== undefined && value !== null) {
        if (value instanceof Array) {
          value = `[${value.map(encodeURIComponent).join(',')}]`;
        }
        const arg = encodeURIComponent(key) + '=' + encodeURIComponent(value);
        args.push(arg);
      }
    });
    if (args.length > 0) {
      url += '?' + args.join('&');
    }
  }
  return [url, options];
}

export function getCurrentUser(then) {
  fetchData('GET', '/api/me', then, then);
}

export function excludedSpread(props, excludes) {
  excludes = excludes || [];
  props = {...props};
  for (const propName of excludes) {
    delete props[propName];
  }
  return props;
}
