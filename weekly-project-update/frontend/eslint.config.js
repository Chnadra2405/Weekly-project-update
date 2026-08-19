import js from "@eslint/js";
import globals from "globals";
import react from "eslint-plugin-react";
import hooks from "eslint-plugin-react-hooks";
import refresh from "eslint-plugin-react-refresh";

export default [
  { ignores: ["dist", "coverage"] },
  {
    files: ["**/*.{js,jsx}"],
    languageOptions: { ecmaVersion: 2022, globals: { ...globals.browser, ...globals.node }, parserOptions: { ecmaFeatures: { jsx: true } } },
    plugins: { react, "react-hooks": hooks, "react-refresh": refresh },
    rules: { ...js.configs.recommended.rules, ...react.configs.recommended.rules, ...react.configs["jsx-runtime"].rules, ...hooks.configs.recommended.rules, ...refresh.configs.vite.rules, "react/prop-types": "off" },
    settings: { react: { version: "detect" } },
  },
];