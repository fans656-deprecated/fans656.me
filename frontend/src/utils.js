// month - 1-based, i.e. 1 for January, 2 for February...
const daysInMonth = (year, month) => new Date(year, month, 0).getDate();

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
