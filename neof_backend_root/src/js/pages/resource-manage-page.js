import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";
import restRead, { restDelete } from "../api/rest-api-consumation";
import {
  Modal,
  ModalCallButton,
  ModalSubmitButton,
} from "../components/modal-components";
import CreateForm from "../components/form-components";
import {
  CardContainerResponsivenessWrapper,
  CardContainer,
} from "../components/card-components";
import {
  PostTableResponsivenessWrapper,
  PostTable,
} from "../components/post-components";
import {
  ButtonResponsivenessWrapper,
  DeleteButton,
  Button,
} from "../components/button-components";

import { objectIsEmpty } from "../utils/dictionary-utils";

const ResourceManagePage = () => {
  const detailResource = window.props.detailResource;
  const listResource = window.props.listResource;

  return (
    <React.StrictMode>
      <>
        {objectIsEmpty(detailResource) ? null : (
          <>
            <ButtonResponsivenessWrapper>
              <Button
                style={detailResource.style}
                label="Back"
                onClick={() => {
                  window.location.href = `${detailResource.refererUrl}`;
                }}
              />
            </ButtonResponsivenessWrapper>
            <DetailResource props={detailResource} />
          </>
        )}
        {objectIsEmpty(listResource) ? null : (
          <ListResource props={listResource} />
        )}
        {null}
      </>
    </React.StrictMode>
  );
};

const DetailResource = ({ props }) => {
  const { style, url, refererUrl } = props;
  return (
    <React.StrictMode>
      <>
        <ButtonResponsivenessWrapper>
          <DeleteButton
            style={style}
            onClick={() => {
              restDelete({
                url: url,
              });
              window.location.href = `${refererUrl}`;
            }}
          />
        </ButtonResponsivenessWrapper>
      </>
    </React.StrictMode>
  );
};
DetailResource.propTypes = {
  props: PropTypes.object,
  style: PropTypes.string,
  url: PropTypes.string,
  refererUrl: PropTypes.string,
};

const ListResource = ({ props }) => {
  const { viewType, style, type, excludeFromResource, urls, createFields } =
    props;
  const formId = "createForm";
  const dataStates = {};
  Object.entries(urls).forEach(([urlName, url]) => {
    const [data, callback] = useState([]);
    dataStates[urlName] = {
      url: url,
      data: data,
      callback: callback,
    };
  });

  let listUpdateCondition = 0;
  useEffect(async () => {
    Object.entries(dataStates).forEach(async ([, dataState], index) => {
      // retrieveDataState(dataState)
      const [
        ,
        // status
        json,
      ] = await restRead({
        url: `${dataState.url}`,
      });
      const setState = dataState.callback;
      console.log("  settings state", index, dataState.url, "to", json);
      setState(() => json);
    });
  }, []);
  // }, [listUpdateCondition]);

  const retrieveDataState = async (dataState) => {
    const [
      ,
      // status
      json,
    ] = await restRead({
      url: `${dataState.url}`,
    });
    const setState = dataState.callback;
    console.log("settings state", dataState.url, "to", json);
    setState(() => json);
  };

  return (
    <React.StrictMode>
      <>
        <Modal
          id="createModal"
          title={`Create new ${type}`}
          confirmButton={
            <ModalSubmitButton style={style} label={"Create"} formId={formId} />
          }
        >
          <CreateForm
            id={formId}
            dataState={dataStates}
            csrfToken={window.props.csrfToken}
            createFields={createFields}
          />
        </Modal>
        <ButtonResponsivenessWrapper>
          <ModalCallButton
            target="createModal"
            style={style}
            label={`New ${type}`}
          />
          {(() => {
            if (
              type === "NewsfeedBase" &&
              dataStates["resource"].data.length === 0
            ) {
              return (
                <>
                  <Modal
                    id="reuseModal"
                    title={`Reuse existing ${type}`}
                    confirmButton={
                      <ModalSubmitButton
                        style={style}
                        label={"Create"}
                        formId={formId}
                      />
                    }
                  >
                    {/* <CreateForm
                    id={formId}
                    dataState={dataStates["resource"]}
                    csrfToken={window.props.csrfToken}
                    createFields={createFields}
                  /> */}
                  </Modal>
                  <ModalCallButton
                    target="reuseModal"
                    style={style}
                    label="Reuse NewsfeedBase"
                  />
                </>
              );
            }
          })()}
        </ButtonResponsivenessWrapper>
        {(() => {
          switch (viewType) {
            case "cards":
              return (
                <CardContainerResponsivenessWrapper>
                  <CardContainer
                    resourceType={type}
                    style={style}
                    excludeKeys={excludeFromResource}
                    dataForCards={dataStates["resource"].data}
                  />
                </CardContainerResponsivenessWrapper>
              );
            case "postTable":
              return (
                <PostTableResponsivenessWrapper>
                  <PostTable
                    style={style}
                    dataStates={dataStates}
                    updateCondition={listUpdateCondition}
                    excludeKeys={excludeFromResource}
                  />
                </PostTableResponsivenessWrapper>
              );
            default:
              return (
                <div className="alert alert-danger" role="alert">
                  viewType unknown!
                </div>
              );
          }
        })()}
      </>
    </React.StrictMode>
  );
};
ListResource.propTypes = {
  props: PropTypes.object,
  viewType: PropTypes.string,
  style: PropTypes.object,
  type: PropTypes.string,
  excludeFromResource: PropTypes.array,
  urls: PropTypes.arrayOf(PropTypes.string),
  createFields: PropTypes.object,
};

document.addEventListener("DOMContentLoaded", function () {
  ReactDOM.render(React.createElement(ResourceManagePage), window.reactMount);
});
