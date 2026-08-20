import { Extension } from "@tiptap/core";

/**
 * Common misspellings → corrections.
 * Keys must be lowercase; values are the corrected form.
 */
const CORRECTIONS = {
  // Transposition / fat-finger typos
  teh: "the",
  hte: "the",
  tje: "the",
  adn: "and",
  nad: "and",
  acn: "can",
  nto: "not",
  thsi: "this",
  waht: "what",
  taht: "that",
  wiht: "with",
  frmo: "from",
  fomr: "from",
  youre: "you're",
  theyre: "they're",
  hes: "he's",
  shes: "she's",
  weve: "we've",
  theyve: "they've",
  youve: "you've",
  ive: "I've",
  // Common misspellings
  accomodate: "accommodate",
  acheive: "achieve",
  accross: "across",
  agressive: "aggressive",
  apparantly: "apparently",
  apparrent: "apparent",
  begining: "beginning",
  beleive: "believe",
  bussiness: "business",
  calender: "calendar",
  commitee: "committee",
  completly: "completely",
  concious: "conscious",
  definate: "definite",
  definately: "definitely",
  dependancy: "dependency",
  dilemna: "dilemma",
  dissapoint: "disappoint",
  dissapear: "disappear",
  enviroment: "environment",
  existance: "existence",
  foriegn: "foreign",
  fourty: "forty",
  freind: "friend",
  goverment: "government",
  grammer: "grammar",
  harrass: "harass",
  humerous: "humorous",
  independant: "independent",
  knowlege: "knowledge",
  maintenence: "maintenance",
  managment: "management",
  millenium: "millennium",
  neccessary: "necessary",
  negociate: "negotiate",
  noticable: "noticeable",
  occassion: "occasion",
  occurrance: "occurrence",
  occured: "occurred",
  ommit: "omit",
  oppurtunity: "opportunity",
  peice: "piece",
  persue: "pursue",
  privelege: "privilege",
  recieve: "receive",
  recomend: "recommend",
  relevent: "relevant",
  repitition: "repetition",
  rythm: "rhythm",
  seperate: "separate",
  similer: "similar",
  sincerly: "sincerely",
  sofware: "software",
  speach: "speech",
  succesful: "successful",
  sucess: "success",
  temperture: "temperature",
  tendancy: "tendency",
  thier: "their",
  tommorow: "tomorrow",
  transfered: "transferred",
  truely: "truly",
  untill: "until",
  writting: "writing",
  adress: "address",
  agreeement: "agreement",
  arguement: "argument",
  assessement: "assessment",
  developement: "development",
  divsion: "division",
  employe: "employee",
  iniciative: "initiative",
  integreation: "integration",
  perfomance: "performance",
  porject: "project",
  projcet: "project",
  quailty: "quality",
  requirment: "requirement",
  requiremnet: "requirement",
  resposibility: "responsibility",
  scheudule: "schedule",
  schedulle: "schedule",
  stategy: "strategy",
  stragety: "strategy",
  sytems: "systems",
  techincal: "technical",
  udpate: "update",
  upadte: "update",
  weekley: "weekly",
};

export const AutoCorrect = Extension.create({
  name: "autocorrect",

  addKeyboardShortcuts() {
    return {
      Space: () => applyAutoCorrect(this.editor, " "),
    };
  },
});

function applyAutoCorrect(editor, insertChar) {
  const { state } = editor;
  const { selection } = state;
  const { $from } = selection;

  if ($from.parentOffset === 0) return false;

  // Text in the current block node up to the cursor
  const textBefore = $from.parent.textContent.slice(0, $from.parentOffset);

  // Match the last contiguous non-space sequence
  const match = textBefore.match(/(\S+)$/);
  if (!match) return false;

  const typed = match[1];
  const correction = CORRECTIONS[typed.toLowerCase()];
  if (!correction) return false;

  // Preserve ALL-CAPS form if the user typed in all-caps
  const corrected =
    typed === typed.toUpperCase() && typed.length > 1
      ? correction.toUpperCase()
      : correction;

  const from = $from.pos - typed.length;
  const to = $from.pos;

  editor.chain().deleteRange({ from, to }).insertContentAt(from, corrected + insertChar).run();
  return true; // consumed the Space key
}
