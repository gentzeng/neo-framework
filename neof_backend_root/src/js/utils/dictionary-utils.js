export { toKeyValueArray as default };

export const filterExcludeKeys = (dictionary, excludeKeys) => {
  let dictionaryFiltered = Object.keys(dictionary)
    .filter((key) => !excludeKeys.includes(key))
    .reduce((cur, key) => {
      return Object.assign(cur, { [key]: dictionary[key] });
    }, {});
  return dictionaryFiltered;
};

export const toKeyValueArray = (dictionary) => {
  let entriesArray = Object.entries(dictionary).map(([key, value]) => [
    key,
    value,
  ]);
  return entriesArray;
};

export const objectIsEmpty = (obj) => {
  return (
    obj &&
    Object.keys(obj).length === 0 &&
    Object.getPrototypeOf(obj) === Object.prototype
  );
};

export const formDataToObject = (formData) => {
  let object = {};
  formData.forEach((value, key) => (object[key] = value));
  return object;
};

export const formDataToJson = (formData) => {
  return JSON.stringify(formDataToObject(formData));
};
