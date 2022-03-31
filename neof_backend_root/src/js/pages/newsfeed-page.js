import React, { useState, useEffect } from "react";
import ReactDOM from "react-dom";
import PropTypes from "prop-types";
import restRead from "../api/rest-api-consumation";
// import { filterExcludeKeys, toKeyValueArray } from "../utils/dictionary-utils";
import { Post, PostResponsivenessWrapper } from "../components/fb-components";

const Newsfeed = () => {
  const { style, excludeFromResource, url } = window.props;

  const [newsfeedData, setNewsfeedData] = useState([]);
  console.log(url);

  useEffect(async () => {
    const [
      ,
      //status
      json,
    ] = await restRead({
      url: `${url}`,
    });
    setNewsfeedData(() => json);
  }, []);
  return (
    <React.StrictMode>
      <>
        <PostResponsivenessWrapper>
          {newsfeedData.map((postData) => {
            // const postDataFiltered = filterExcludeKeys(postData,);
            // const postDataFilteredAsArray = toKeyValueArray(postData);
            return (
              <Post key={postData.id} _key={postData.id} postData={postData} />
            );
          })}
        </PostResponsivenessWrapper>
      </>
    </React.StrictMode>
  );
};
Newsfeed.propTypes = {
  props: PropTypes.object,
  style: PropTypes.object,
  excludeFromResource: PropTypes.array,
  url: PropTypes.string,
};

document.addEventListener("DOMContentLoaded", function () {
  ReactDOM.render(React.createElement(Newsfeed), window.reactMount);
});
