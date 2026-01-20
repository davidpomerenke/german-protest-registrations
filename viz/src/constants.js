// Topic categories from categorization schema
export const TOPIC_CATEGORIES = [
  "Climate Protection",
  "Energy Transition",
  "Nuclear Issues",
  "COVID-19 Measures",
  "COVID-19 Skepticism",
  "Anti-War / Peace",
  "Ukraine Conflict",
  "Syria Conflict",
  "Afghanistan",
  "Labor Rights / Strikes",
  "Healthcare Workers",
  "Education",
  "Migration / Refugees",
  "Housing / Rent",
  "Animal Rights",
  "Veganism",
  "Environment / Nature",
  "Anti-Racism",
  "Anti-Fascism",
  "Far-Right / PEGIDA / AfD",
  "Feminism / Women's Rights",
  "LGBTQ+ Rights",
  "Social Justice / Poverty",
  "Democracy / Civil Rights",
  "Surveillance / Privacy",
  "Palestine / Israel",
  "Kurdistan / PKK",
  "Turkey Politics",
  "Iran",
  "China / Hong Kong",
  "Tibet",
  "Latin America",
  "Religious Issues",
  "Antisemitism",
  "Remembrance / Memorial",
  "May Day / Labor Day",
  "Gentrification / Urban Development",
  "Transportation / Mobility",
  "Agriculture / Farming",
  "EU Politics",
  "Elections / Campaigns"
];

// Color palette for topics (grouped by theme)
export const TOPIC_COLORS = {
  // Environment (greens)
  "Climate Protection": "#2d6a4f",
  "Energy Transition": "#40916c",
  "Nuclear Issues": "#52b788",
  "Environment / Nature": "#74c69d",
  "Agriculture / Farming": "#95d5b2",

  // COVID (purples)
  "COVID-19 Measures": "#7b2cbf",
  "COVID-19 Skepticism": "#9d4edd",

  // Peace & Conflict (blues)
  "Anti-War / Peace": "#1d3557",
  "Ukraine Conflict": "#457b9d",
  "Syria Conflict": "#a8dadc",
  "Afghanistan": "#219ebc",

  // Labor (oranges)
  "Labor Rights / Strikes": "#e85d04",
  "Healthcare Workers": "#f48c06",
  "May Day / Labor Day": "#faa307",

  // Social (reds/pinks)
  "Education": "#c9184a",
  "Migration / Refugees": "#ff4d6d",
  "Housing / Rent": "#ff758f",
  "Social Justice / Poverty": "#ff8fa3",
  "Gentrification / Urban Development": "#ffb3c1",

  // Rights (warm colors)
  "Animal Rights": "#9d0208",
  "Veganism": "#d00000",
  "Anti-Racism": "#dc2f02",
  "Anti-Fascism": "#e85d04",
  "Feminism / Women's Rights": "#f72585",
  "LGBTQ+ Rights": "#b5179e",

  // Politics (teals/cyans)
  "Far-Right / PEGIDA / AfD": "#023047",
  "Democracy / Civil Rights": "#0077b6",
  "Surveillance / Privacy": "#00b4d8",
  "EU Politics": "#48cae4",
  "Elections / Campaigns": "#90e0ef",

  // International (earth tones)
  "Palestine / Israel": "#6c584c",
  "Kurdistan / PKK": "#a98467",
  "Turkey Politics": "#adc178",
  "Iran": "#dda15e",
  "China / Hong Kong": "#bc6c25",
  "Tibet": "#606c38",
  "Latin America": "#283618",

  // Other
  "Religious Issues": "#7f5539",
  "Antisemitism": "#9c6644",
  "Remembrance / Memorial": "#582f0e",
  "Transportation / Mobility": "#3a86a7",
};

export const DEFAULT_COLOR = "#6c757d";

export const getTopicColor = (topics) => {
  if (!topics || topics.length === 0) return DEFAULT_COLOR;
  // Return color of first topic
  return TOPIC_COLORS[topics[0]] || DEFAULT_COLOR;
};

// Cities list
export const CITIES = [
  "Berlin", "München", "Köln", "Dresden", "Bremen", "Freiburg",
  "Mainz", "Erfurt", "Kiel", "Magdeburg", "Karlsruhe", "Wiesbaden",
  "Duisburg", "Saarbrücken", "Dortmund", "Wuppertal", "Potsdam"
];
