// Translations for rrules.js

export const SPANISH = {
  dayNames: [
    'domingo', 'lunes', 'martes', 'miércoles',
    'jueves', 'viernes', 'sábado'
  ],
  monthNames: [
    'enero', 'febrero', 'marzo', 'abril', 'mayo',
    'junio', 'julio', 'agosto', 'septiembre', 'octubre',
    'noviembre', 'diciembre'
  ],
  tokens: {
    'SKIP': /^[ \r\n\t]+|^\.$/,
    'number': /^[1-9][0-9]*/,
    'numberAsText': /^(one|two|three)/i,
    'every': /^every/i,
    'day(s)': /^days?/i,
    'weekday(s)': /^weekdays?/i,
    'week(s)': /^weeks?/i,
    'hour(s)': /^hours?/i,
    'month(s)': /^months?/i,
    'year(s)': /^years?/i,
    'on': /^(on|in)/i,
    'at': /^(at)/i,
    'the': /^the/i,
    'first': /^first/i,
    'second': /^second/i,
    'third': /^third/i,
    'nth': /^([1-9][0-9]*)(\.|th|nd|rd|st)/i,
    'last': /^last/i,
    'for': /^for/i,
    'time(s)': /^times?/i,
    'until': /^(un)?til/i,
    'monday': /^mo(n(day)?)?/i,
    'tuesday': /^tu(e(s(day)?)?)?/i,
    'wednesday': /^we(d(n(esday)?)?)?/i,
    'thursday': /^th(u(r(sday)?)?)?/i,
    'friday': /^fr(i(day)?)?/i,
    'saturday': /^sa(t(urday)?)?/i,
    'sunday': /^su(n(day)?)?/i,
    'january': /^jan(uary)?/i,
    'february': /^feb(ruary)?/i,
    'march': /^mar(ch)?/i,
    'april': /^apr(il)?/i,
    'may': /^may/i,
    'june': /^june?/i,
    'july': /^july?/i,
    'august': /^aug(ust)?/i,
    'september': /^sep(t(ember)?)?/i,
    'october': /^oct(ober)?/i,
    'november': /^nov(ember)?/i,
    'december': /^dec(ember)?/i,
    'comma': /^(,\s*|(and|or)\s*)+/i
  }
}

const esStrings = {
  'every': 'cada',
  'day': 'día',
  'days': 'días',
  'weekday': 'día laborable',
  'week': 'semana',
  'weeks': 'semanas',
  'hour': 'hora',
  'hours': 'hora',
  'month': 'mes',
  'months': 'meses',
  'year': 'año',
  'years': 'años',
  'on': 'los',
  'at': 'en',
  'the': 'el',
  'first': 'primero',
  'second': 'segundo',
  'third': 'tercer',
  'last': 'último',
  'for': 'por',
  'time': 'vez',
  'times': 'veces',
  'until': 'hasta',
};

export function gettext(id) {
  // Returns es string, default to english
  return esStrings[id] || id;
}
