import _ from "lodash";
import React from "react";
import PropTypes from "prop-types";
import { useTable } from "react-table";
import { DndProvider, useDrag, useDrop } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { filterExcludeKeys, objectIsEmpty } from "../utils/dictionary-utils";
import { restRead, restUpdateJson } from "../api/rest-api-consumation";
import update from "immutability-helper";
import {
  ButtonResponsivenessWrapper,
  Button,
  FormSubmitButton,
} from "../components/button-components";

export { PostTable as default };

const MAX_STRING_LENGTH = 25;

class RenderingIncompleteError extends Error {
  constructor(message) {
    super(message);
    this.name = "RenderingIncompleteError";
  }
}

export const PostTableResponsivenessWrapper = ({ children }) => {
  return (
    <React.StrictMode>
      <div className="table-responsive table-wrapper-scroll-y m-auto">
        {children}
      </div>
    </React.StrictMode>
  );
};
PostTableResponsivenessWrapper.propTypes = {
  children: PropTypes.node,
};

const emptyRowKeys = [
  "id",
  "user",
  "resource_url",
  "manage_url",
  "type",
  "article_url",
  "image_url",
  "image",
  "splash_image_url",
  "splash_image",
  "header",
  "title",
  "content",
  "first_reaction",
  "second_reaction",
  "third_reaction",
  "newsfeed_base",
  "time_created",
  "time_updated",
];

export const PostTable = React.memo(
  ({ style, dataStates, updateCondition, excludeKeys }) => {
    console.log("rendering");
    for (let dataState in dataStates) {
      const data = dataStates[dataState].data;
      if (
        typeof data == "undefined" ||
        data.length === 0 ||
        objectIsEmpty(data)
      ) {
        return null;
      }
    }

    const resourceUrl = dataStates["resource"].url;
    const postStateData = dataStates["resource"].data;
    const setPostStateData = dataStates["resource"].callback;

    const newsfeedBase = dataStates["newsfeedBase"].data;
    const setNewsfeedBase = dataStates["newsfeedBase"].callback;

    const newsfeedSize = newsfeedBase.newsfeed_size;
    const newsfeedBaseId = newsfeedBase.id;
    const newsfeedBaseUrl = newsfeedBase.resource_url;
    const postOrder = newsfeedBase.post_order;
    let postData = [];

    try {
      postData = createPostData(newsfeedSize, postOrder, postStateData);
    } catch (e) {
      if (e instanceof RenderingIncompleteError) {
        return null;
      }
    }

    const [originalPostData] = React.useState(postData);
    const resetToOriginalPostData = () => setPostStateData(originalPostData);

    const columnsData = createColumnsData(postData, excludeKeys);
    const columns = React.useMemo(() => columnsData, []);

    const defaultColumn = {
      // Set our editable cell renderer as the default Cell renderer
      Cell: EditableCell,
    };

    const getRowId = React.useCallback((row) => {
      return row.id;
    }, []);

    const updateData = (rowIndex, columnId, value) => {
      console.log("*** updataData ***", postStateData);
      console.log("*** updateData ***", rowIndex, columnId, value);
      setPostStateData((old) =>
        old.map((row, index) => {
          console.log("  *** updateData ***", index, row);

          if (index === rowIndex) {
            const ret = {
              ...old[rowIndex],
              [columnId]: value,
            };
            console.log(
              "    *** updateData index equal***",
              index,
              rowIndex,
              ret
            );
            return ret;
          }
          console.log("  *** updateData return row***", index, rowIndex, row);
          return row;
        })
      );
    };

    const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
      useTable({
        data: postData,
        columns,
        defaultColumn,
        getRowId,
        updateData,
        initialState: {
          hiddenColumns: ["id"],
        },
      });

    const updatePostStateData = React.useCallback(async (event) => {
      event.preventDefault(); // prevent default behavior of form submit
      const formDataRaw = new FormData(event.target);
      let data = [];
      formDataRaw.forEach((value, key) => {
        const inputIdRegxp = /^(\w+)--\w+$/;
        const inputNameRegExp = /^\w+--(\w+)$/;
        const inputId = parseInt(key.replace(inputIdRegxp, "$1"));
        const inputName = key.replace(inputNameRegExp, "$1");

        if (data[inputId] == null) {
          data.push({});
        }
        data[inputId][`${inputName}`] = value;
      });

      data = data
        .filter((row) => !row.id.startsWith("empty"))
        .map((row) => {
          row.order_in_newsfeed_base = {
            newsfeed_base_id: newsfeedBaseId,
            index: row.order_in_newsfeed_base,
          };

          return row;
        });

      console.log("      updatePostStateData date without empty entries", data);
      const [
        ,
        // status
        jsonData,
      ] = await restUpdateJson({
        url: resourceUrl,
        data: JSON.stringify(data),
      });

      console.log("      updatePostStateData updated json Data", jsonData);
      const [, jsonNewsfeedBase] = await restRead({
        url: newsfeedBaseUrl,
      });

      console.log(
        "      updatePostStateData get newsfeedBase with new order",
        jsonNewsfeedBase
      );
      setNewsfeedBase(() => jsonNewsfeedBase);
      setPostStateData(() => jsonData);
      console.log("      updatePostStateData updating condition");
      // updateCondition += 1;
    });

    const moveRow = async (dragIndex, hoverIndex) => {
      const dragRecord = postData[dragIndex];
      const newData = update(postData, {
        $splice: [
          [dragIndex, 1],
          [hoverIndex, 0, dragRecord],
        ],
      });
      const newPostOrder = {
        order: [],
        value_to_key: {},
      };

      newData.map((dataEntry, index) => {
        if (
          typeof dataEntry.id == "string" &&
          dataEntry.id.startsWith("empty")
        ) {
          newPostOrder.order.push(null);
        } else {
          newPostOrder.order.push(dataEntry.id);
          newPostOrder.value_to_key[dataEntry.id] = index;
        }
      });

      const [, json] = await restUpdateJson({
        url: newsfeedBaseUrl,
        data: JSON.stringify({ post_order: newPostOrder }),
      });

      setNewsfeedBase(() => json);
      setPostStateData(() => newData);
    };

    const formId = "updateForm";
    return (
      <React.StrictMode>
        <ButtonResponsivenessWrapper>
          {/* ToDo use label variable  */}
          <Button
            style={style}
            label={"Reset manual posts"}
            onClick={resetToOriginalPostData}
          />
          <FormSubmitButton
            formId={formId}
            style={style}
            label={"Update manual posts"}
          />
        </ButtonResponsivenessWrapper>
        <DndProvider backend={HTML5Backend}>
          <form onSubmit={updatePostStateData} id={formId}>
            <table
              className={`table table-${style.color} table-striped`}
              {...getTableProps()}
            >
              <thead>
                {headerGroups.map((headerGroup, index) => {
                  return (
                    <tr key={index} {...headerGroup.getHeaderGroupProps()}>
                      <th
                        {...headerGroups[0].headers[0].getHeaderProps({
                          style: {
                            minWidth: 4,
                            maxWidth: 4,
                            width: 4,
                          },
                        })}
                      ></th>
                      {headerGroup.headers.map((column, index) => {
                        return (
                          <th
                            key={index}
                            {...column.getHeaderProps({
                              style: {
                                minWidth: column.minWidth,
                                maxWidth: column.maxWidth,
                                width: column.width,
                              },
                            })}
                          >
                            {column.render("Header")}
                          </th>
                        );
                      })}
                    </tr>
                  );
                })}
              </thead>
              <tbody {...getTableBodyProps()}>
                {rows.map((row, index) => {
                  return (
                    prepareRow(row) || (
                      <Row
                        id={row.id}
                        index={index}
                        row={row}
                        moveRow={moveRow}
                        manageUrl={row.original.manage_url}
                        {...row.getRowProps()}
                      ></Row>
                    )
                  );
                })}
              </tbody>
            </table>
          </form>
        </DndProvider>
      </React.StrictMode>
    );
  },
  (prevProps, nextProps) => {
    const prevPostStateData = prevProps.dataStates["resource"].data;
    const prevNewsfeedBase = prevProps.dataStates["newsfeedBase"].data;
    const nextPostStateData = nextProps.dataStates["resource"].data;
    const nextNewsfeedBase = nextProps.dataStates["newsfeedBase"].data;
    // if (nextNewsfeedBase === []) {
    //   return true
    // }
    console.log("******************");
    console.log("prevPostStateData", prevPostStateData);
    console.log("nextPostStateData", nextPostStateData);
    console.log(
      "postStateDataEqual",
      _.isEqual(prevPostStateData, nextPostStateData)
    );
    console.log("prevNewsfeedBase", prevNewsfeedBase);
    console.log("nextNewsfeedBase", nextNewsfeedBase);
    console.log(
      "newsfeedBaseEqual",
      _.isEqual(prevNewsfeedBase, nextNewsfeedBase)
    );
    return _.isEqual(prevProps, nextProps);
  }
);
PostTable.propTypes = {
  style: PropTypes.object,
  dataStates: PropTypes.object,
  resourceUrl: PropTypes.string,
  postStateData: PropTypes.array,
  setPostStateData: PropTypes.func,
  updateCondition: PropTypes.number,
  excludeKeys: PropTypes.array,
};

const createPostData = (newsfeedSize, postOrder, postStateData) => {
  const rawPosts = {};
  postStateData.map((dataEntry) => {
    rawPosts[dataEntry.id] = dataEntry;
  });

  const postData = [];
  for (let i = 0; i < newsfeedSize; i++) {
    const postOrderId = postOrder["order"][i];
    if (postOrderId != null) {
      const rawPost = rawPosts[postOrderId];
      if (rawPost == undefined) {
        throw new RenderingIncompleteError();
      }
      postData.push(rawPost);
    } else {
      const emptyRow = {};
      emptyRowKeys.map((key) => {
        if (key === "id") {
          emptyRow[key] = "empty" + i;
        } else {
          emptyRow[key] = i;
        }
      });
      postData.push({ ...emptyRow });
    }
  }
  console.log("    -------------------------------------");
  console.log("    createPostData postOrder", postOrder);
  console.log("    createPostData postStateData", postStateData);
  console.log("    createPostData postData", postData);
  return postData;
};

const createColumnsData = (postData, excludeKeys) => {
  const tableFirstRowDataFiltered = filterExcludeKeys(postData[0], excludeKeys);
  const tableHeads = Object.keys(tableFirstRowDataFiltered);
  const columnsData = [];

  tableHeads.map((tableHead) => {
    const tableHeadColumn = {
      Header: tableHead,
      accessor: tableHead,
      minWidth: MAX_STRING_LENGTH,
      maxWidth: MAX_STRING_LENGTH,
      width: MAX_STRING_LENGTH,
    };

    if (tableHead.includes("image")) {
      tableHeadColumn.Cell = function tableCellImage(tableProps) {
        const prop = tableProps.row.original[tableHead];
        if (typeof prop == "number") {
          return <></>;
        }
        return (
          <img
            src={tableProps.row.original[tableHead]}
            width="100%"
            alt="image"
          />
        );
      };
    }
    columnsData.push(tableHeadColumn);
  });
  return columnsData;
};

const DND_ITEM_TYPE = "row";

export const Row = ({ id, row, index, moveRow, manageUrl }) => {
  const goToManagePage = () => {
    if (typeof id == "string" && id.startsWith("empty")) {
      return;
    }
    window.location.href = manageUrl;
  };

  const dropRef = React.useRef(null);
  const dragRef = React.useRef(null);

  const [, drop] = useDrop({
    accept: DND_ITEM_TYPE,
    hover(item, monitor) {
      if (!dropRef.current) {
        return;
      }
      const dragIndex = item.index;
      const hoverIndex = index;
      // Don't replace items with themselves
      if (dragIndex === hoverIndex) {
        return;
      }
      // Determine rectangle on screen
      const hoverBoundingRect = dropRef.current.getBoundingClientRect();
      // Get vertical middle
      const hoverMiddleY =
        (hoverBoundingRect.bottom - hoverBoundingRect.top) / 2;
      // Determine mouse position
      const clientOffset = monitor.getClientOffset();
      // Get pixels to the top
      const hoverClientY = clientOffset.y - hoverBoundingRect.top;
      // Only perform the move when the mouse has crossed half of the items height
      // When dragging downwards, only move when the cursor is below 50%
      // When dragging upwards, only move when the cursor is above 50%
      // Dragging downwards
      if (dragIndex < hoverIndex && hoverClientY < hoverMiddleY) {
        return;
      }
      // Dragging upwards
      if (dragIndex > hoverIndex && hoverClientY > hoverMiddleY) {
        return;
      }
      // Time to actually perform the action
      moveRow(dragIndex, hoverIndex);
      // Note: we're mutating the monitor item here!
      // Generally it's better to avoid mutations,
      // but it's good here for the sake of performance
      // to avoid expensive index searches.
      item.index = hoverIndex;
    },
  });

  const [, drag, preview] = useDrag({
    type: DND_ITEM_TYPE,
    item: { type: DND_ITEM_TYPE, index },
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  });

  preview(drop(dropRef));
  drag(dragRef);

  const headCell = row.cells[0];

  return (
    <React.StrictMode>
      <tr className="opacity-50" ref={dropRef} onClick={goToManagePage}>
        <td
          className="cursor-grab"
          ref={dragRef}
          {...headCell.getCellProps({
            style: {
              minWidth: 4,
              maxWidth: 4,
              width: 4,
            },
          })}
        >
          <input type="hidden" name={`${index}--id`} value={id} />
          {/* for ordering and fixed position */}
          <input
            type="hidden"
            name={`${index}--order_in_newsfeed_base`}
            value={index}
          />
          <input
            type="hidden"
            name={`${index}--type`}
            value={row.original.type}
          />
          <input
            type="hidden"
            name={`${index}--article_url`}
            value={row.original.article_url}
          />
          <input
            type="hidden"
            name={`${index}--image_url`}
            value={row.original.image_url}
          />
          <input
            type="hidden"
            name={`${index}--splash_url`}
            value={row.original.splash_url}
          />
          move
        </td>
        {row.cells.map((cell, index) => {
          if (typeof id == "string" && id.startsWith("empty")) {
            return (
              <td
                key={index}
                {...cell.getCellProps({
                  style: {
                    minWidth: cell.column.minWidth,
                    maxWidth: cell.column.maxWidth,
                    width: cell.column.width,
                    cursor: "unset",
                  },
                })}
              ></td>
            );
          }
          return (
            <td
              key={index}
              {...cell.getCellProps({
                style: {
                  minWidth: cell.column.minWidth,
                  maxWidth: cell.column.maxWidth,
                  width: cell.column.width,
                  cursor: "pointer",
                },
              })}
            >
              {cell.render("Cell")}
            </td>
          );
        })}
      </tr>
    </React.StrictMode>
  );
};
Row.propTypes = {
  id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  row: PropTypes.object,
  index: PropTypes.number,
  moveRow: PropTypes.func,
  manageUrl: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
};

// Create an editable cell renderer
const EditableCell = ({
  value: initialValue,
  row: { index },
  column: { id },
  updateData, // This is a custom function that we supplied to our table instance
}) => {
  // We need to keep and update the state of the cell normally
  const [value, setValue] = React.useState(initialValue);

  const onChange = (e) => {
    setValue(e.target.value);
  };

  // We'll only update the external data when the input is blurred
  const onBlur = () => {
    updateData(index, id, value);
  };

  const onClick = (e) => {
    e.stopPropagation();
  };

  // If the initialValue is changed external, sync it up with our state
  React.useEffect(() => {
    setValue(initialValue);
  }, [initialValue]);

  return (
    <input
      value={value}
      name={`${index}--${id}`}
      onChange={onChange}
      onBlur={onBlur}
      onClick={onClick}
    />
  );
};
EditableCell.propTypes = {
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  row: PropTypes.object,
  column: PropTypes.object,
  updateData: PropTypes.func,
};
