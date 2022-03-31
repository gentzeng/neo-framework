export { capitalizeFirstLetter as default };
export const capitalizeFirstLetter = (str) => {
  return str.charAt(0).toUpperCase() + str.slice(1);
};

export const shortenString = (str, maxLength) => {
  return str.length < maxLength ? str : `${str.substr(0, maxLength)} ...}`;
};
