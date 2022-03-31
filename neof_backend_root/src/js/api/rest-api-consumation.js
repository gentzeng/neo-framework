import getCookieValue, {
  openLoginPageIfUnauthorized,
  unauthorizedStatus,
} from "../utils/authentication-utils";

export { restRead as default };

export const restRead = async ({ url = "/", authorize = true } = {}) => {
  return restFetch({
    url: url,
    authorize: authorize,
  });
};

export const restCreate = async ({
  url = "/",
  data = {},
  authorize = true,
} = {}) => {
  return restFetch({
    url: url,
    method: "POST",
    data: data,
    authorize: authorize,
  });
};

export const restUpdate = async ({
  url = "/",
  data = {},
  authorize = true,
} = {}) => {
  return restFetch({
    url: url,
    method: "PUT",
    data: data,
    authorize: authorize,
  });
};

export const restUpdateJson = async ({
  url = "/",
  data = {},
  authorize = true,
} = {}) => {
  return restFetch({
    url: url,
    method: "PUT",
    data: data,
    authorize: authorize,
    contentType: "application/json",
  });
};

export const restDelete = async ({
  url = "/",
  data = {},
  authorize = true,
} = {}) => {
  return restFetch({
    url: url,
    method: "DELETE",
    data: data,
    authorize: authorize,
    contentType: "application/json",
  });
};

export const restFetch = async ({
  url = "/",
  method = "GET",
  data = {},
  authorize = true,
  contentType = "",
} = {}) => {
  let _status = 200;
  let _json = {};
  let headers = {
    Accept: "application/json",
    Authorization: authorize ? "Token " + getCookieValue("auth_token") : null,
  };

  if (contentType !== "") {
    headers["Content-Type"] = contentType;
  }

  await fetch(url, {
    method: method,
    headers: headers,
    body: ["GET"].includes(method) ? null : data,
  })
    .then((response) => {
      if (authorize) {
        openLoginPageIfUnauthorized(response);
      }
      _status = response.status;
      return response.json();
    })
    .then((json) => {
      if (unauthorizedStatus(_status)) {
        return;
      }
      _json = json;
    });
  // .catch((error) => console.error(error));

  return [_status, _json];
};
