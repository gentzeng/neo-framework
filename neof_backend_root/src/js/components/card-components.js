import React from "react";
import PropTypes from "prop-types";
import { filterExcludeKeys, toKeyValueArray } from "../utils/dictionary-utils";
import KeyValueTable from "../components/table-components";
import { objectIsEmpty } from "../utils/dictionary-utils";
import { shortenString } from "../utils/string-utils";

export { CardContainer as default };

export const CardContainerResponsivenessWrapper = ({ children }) => {
  return (
    <React.StrictMode>
      <div className="row row-cols-xxl-4 row-cols-xl-3 row-cols-lg-3 row-cols-md-2 row-cols-sm-1 row-cols-1 mt-0 mb-3 mx-auto g-4">
        {children}
      </div>
    </React.StrictMode>
  );
};
CardContainerResponsivenessWrapper.propTypes = {
  children: PropTypes.node,
};

export const CardContainer = ({
  resourceType,
  style,
  dataForCards,
  excludeKeys,
}) => {
  console.log("CardContainer", dataForCards);
  if (
    typeof dataForCards == "undefined" ||
    dataForCards.length === 0 ||
    objectIsEmpty(dataForCards)
  ) {
    return null;
  }
  return (
    <React.StrictMode>
      <>
        {dataForCards.map((cardData) => {
          const cardDataFiltered = filterExcludeKeys(cardData, excludeKeys);
          const cardDataFilteredAsArray = toKeyValueArray(cardDataFiltered);
          return (
            <Card
              key={cardData.id}
              _key={cardData.id}
              id={cardData.id}
              title={cardData.name}
              description={cardData.description}
              resourceType={resourceType}
              style={style}
              manageUrl={cardData.manage_url}
              cardData={cardDataFilteredAsArray}
            />
          );
        })}
      </>
    </React.StrictMode>
  );
};
CardContainer.propTypes = {
  resourceType: PropTypes.string,
  style: PropTypes.object,
  dataForCards: PropTypes.array,
  excludeKeys: PropTypes.array,
};

export const Card = ({
  _key,
  id,
  title,
  description,
  resourceType,
  style,
  manageUrl,
  cardData,
}) => {
  const ref = React.useRef(null);

  const goToManagePage = () => {
    window.location.href = manageUrl;
  };

  return (
    <React.StrictMode>
      <div className="col mt-0 mb-3" key={_key} onClick={goToManagePage}>
        <input type="hidden" ref={ref} value={id} />
        <div
          className={`card cursor-pointer h-100 mb-3 ${style.textColor} bg-${style.color}`}
          id={`${resourceType}Card${id}`}
        >
          <CardHeader resourceType={resourceType} title={title} id={id} />
          <CardBody
            description={description}
            cardData={cardData}
            style={style}
          />
        </div>
      </div>
    </React.StrictMode>
  );
};
Card.propTypes = {
  _key: PropTypes.number,
  id: PropTypes.number,
  title: PropTypes.string,
  description: PropTypes.string,
  resourceType: PropTypes.string,
  style: PropTypes.object,
  manageUrl: PropTypes.string,
  cardData: PropTypes.array,
};

export const CardHeader = ({ resourceType, title, id }) => {
  return (
    <React.StrictMode>
      <div className="card-header" value={id}>
        {`${
          resourceType.substring(0, 1).toUpperCase() + resourceType.substring(1)
        }: ${title}`}
      </div>
    </React.StrictMode>
  );
};
CardHeader.propTypes = {
  resourceType: PropTypes.string,
  title: PropTypes.string,
  id: PropTypes.number,
};

export const CardBody = ({ description, cardData, style }) => {
  const maxDescriptionLength = 128;
  let descriptionShortened = "";
  if (description) {
    descriptionShortened = shortenString(description, maxDescriptionLength);
  }
  return (
    <React.StrictMode>
      <div className="card-body pb-0">
        <div className="card-text">
          <KeyValueTable keyValues={cardData} style={style} />
        </div>
        <h6 className="card-title">{descriptionShortened}</h6>
      </div>
    </React.StrictMode>
  );
};
CardBody.propTypes = {
  description: PropTypes.string,
  cardData: PropTypes.array,
  style: PropTypes.object,
};
