var gulp = require("gulp"),
  babelify = require("babelify"),
  browserify = require("browserify"),
  source = require("vinyl-source-stream"),
  buffer = require("vinyl-buffer");

const buildSrcJs = function ({
  srcFile = "",
  srcPath = ".",
  dstPath = ".",
} = {}) {
  return browserify(srcPath + srcFile)
    .transform(
      babelify.configure({
        presets: [
          "@babel/preset-react",
          "@babel/preset-env",
          {
            plugins: ["@babel/plugin-transform-runtime"],
          },
        ],
      })
    )
    .bundle()
    .pipe(source(srcFile))
    .pipe(gulp.dest(dstPath));
  //.pipe(buffer())     // You need this if you want to continue using the stream with other plugins
};

const buildResourceManagePage = function () {
  return buildSrcJs({
    srcFile: "resource-manage-page.js",
    srcPath: "./neof_backend_root/src/js/pages/",
    dstPath: "./neof_backend_root/static/js/pages/",
  });
};

const buildAuthPage = function () {
  return buildSrcJs({
    srcFile: "auth-page.js",
    srcPath: "./neof_backend_root/src/js/pages/",
    dstPath: "./neof_backend_root/static/js/pages/",
  });
};

const buildNewsfeedPage = function () {
  return buildSrcJs({
    srcFile: "newsfeed-page.js",
    srcPath: "./neof_backend_root/src/js/pages/",
    dstPath: "./neof_backend_root/static/js/pages/",
  });
};

exports.default = buildResourceManagePage;

exports.buildResourceManagePage = buildResourceManagePage;
exports.buildAuthPage = buildAuthPage;
exports.buildNewsfeedPage = buildNewsfeedPage;
exports.build = gulp.series(
  buildResourceManagePage,
  buildAuthPage,
  buildNewsfeedPage
);

// index.html
// <script src="dist/bundle.js></script>
