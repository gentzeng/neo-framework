import React from "react";
import PropTypes from "prop-types";
export { KeyValueTable as default };

export const KeyValueTable = ({ keyValues, style }) => {
  return (
    <React.StrictMode>
      <table className={`table table-borderless ${style.textColor}`}>
        <tbody>
          {keyValues.map((entry) => {
            return <KeyValueTableRow key={entry[0]} entry={entry} />;
          })}
        </tbody>
      </table>
    </React.StrictMode>
  );
};
KeyValueTable.propTypes = {
  keyValues: PropTypes.array,
  style: PropTypes.object,
};

export const KeyValueTableRow = ({ entry }) => {
  return (
    <React.StrictMode>
      <tr key={entry[0]}>
        <th scope="row">{entry[0]}</th>
        <td>{entry[1]}</td>
      </tr>
    </React.StrictMode>
  );
};
KeyValueTableRow.propTypes = {
  entry: PropTypes.array,
};
