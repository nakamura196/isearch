<template>
  <v-app>
    <v-app-bar>
      <v-toolbar-title>{{config.header}}</v-toolbar-title>
    </v-app-bar>
    <v-content>
      <v-container>
        <v-card class="my-5">
          <v-card-text>
            <v-text-field
              v-on:keyup.enter="search_move"
              v-model="advancedSearch['Full text search']"
              label="Full text search"
            ></v-text-field>

            <v-btn color="primary" @click="search_move">Search</v-btn>
            <v-btn class="ml-4" @click="reset">Reset</v-btn>
          </v-card-text>
        </v-card>
      </v-container>

      <div style="background-color: #eeeeee;" class="pb-5">
        <v-container>
          <v-row>
            <v-col cols="12" sm="3">
              <h3>{{((query.page - 1) * query.size + 1).toLocaleString()}} - {{(query.page * query.size > total ? total : query.page * query.size).toLocaleString()}} of {{total.toLocaleString()}} results</h3>
            </v-col>
            <v-col cols="12" sm="9">
              <v-row>
                <v-col>
                  <v-select
                    :items="computed_itemsSort"
                    v-model="query.sort"
                    label="Sort by"
                    @change="sort_move"
                  ></v-select>
                </v-col>

                <v-col>
                  <v-select
                    :items="[20, 50, 100]"
                    v-model="query.size"
                    label="Items per page"
                    @change="size_move"
                  ></v-select>
                </v-col>

                <v-col>
                  <span class="mr-2">Layout</span>

                  <v-btn-toggle
                    v-model="layout"
                    mandatory
                  >
                    <v-btn>
                      <i class='fas fa-th-large'></i>
                    </v-btn>
                    <v-btn>
                      <i class='fas fa-th-list'></i>
                    </v-btn>
                  </v-btn-toggle>
                </v-col>
              </v-row>
            </v-col>
          </v-row>

          <v-card outlined style="background-color: #eeeeee;">
            <v-card-text>
              <span class="mr-2">Filtered by</span>

              <span :key="'a_'+key" v-for="(value, key) in advancedSearchDisplay">
                <!-- display重要 -->
                <v-btn
                  color="primary"
                  small
                  class="mx-1 my-1"
                  @click="advancedSearch[key] = ''; search(true)"
                  v-if="value != [] && value != ''"
                >
                  [Advanced] {{key.replace(".keyword", "")}}:
                  <b
                    class="mx-2"
                    :class="key == 'Phone/Word' ? 'phone' : ''"
                  >{{value instanceof Array ? value.join(", ") : value}}</b>
                  <span aria-hidden="true">&times;</span>
                </v-btn>
              </span>

              <span :key="'f_'+key" v-for="(value, key) in facetSearch">
                <v-btn
                  color="primary"
                  small
                  class="mx-1 my-1"
                  @click="facetSearch[key] = ''; search(true)"
                  v-if="value != [] && value != ''"
                >
                  [Facet] {{key.replace(".keyword", "")}}:
                  <b
                    class="mx-2"
                    :class="key == 'Phone/Word' ? 'phone' : ''"
                  >{{value instanceof Array ? value.join(", ") : value}}</b>
                  <span aria-hidden="true">&times;</span>
                </v-btn>
              </span>
            </v-card-text>
          </v-card>
        </v-container>
      </div>

      <v-container class="mt-5">
        <v-row>
          <v-col cols="12" sm="3" style="background-color: #eeeeee;">
            <template v-if="total > 0">
              <h3 class="mb-5">Refine your search</h3>
              <template v-for="(obj, index) in results.aggregations">
                <v-card
                  class="my-5"
                  :key="'agg_'+index"
                  outlined
                  v-if="index != 'Full text search' && obj.buckets.length > 0">
                  <v-list subheader two-line flat>
                    <v-subheader>{{index}}</v-subheader>

                    <div style="max-height: 400px; overflow-y:auto;">
                      <v-list-item-group multiple>
                        <template v-for="(bucket, index2) in obj.buckets">
                          <v-list-item :key="'bucket_'+index2" v-if="bucket.key != ''">
                            <template>
                              <v-list-item-action>
                                <v-checkbox v-model="bucket.value" color="primary"></v-checkbox>
                              </v-list-item-action>

                              <v-list-item-content>
                                <v-list-item-title
                                  :class="index == 'Phone/Word' ? 'phone' : ''"
                                >{{bucket.key}}</v-list-item-title>
                              </v-list-item-content>

                              <v-list-item-action>
                                <v-btn icon>{{bucket.doc_count}}</v-btn>
                              </v-list-item-action>
                            </template>
                          </v-list-item>
                        </template>
                      </v-list-item-group>
                    </div>
                    <v-card-text>
                      <v-btn small color="primary" @click="facet_filter">Search</v-btn>
                    </v-card-text>
                  </v-list>
                </v-card>
              </template>
            </template>
          </v-col>
          <v-col cols="12" sm="9">
            <template v-if="total > 0">
              <div class="text-center">
                <v-pagination
                  v-model="query.page"
                  :length="pagination_length"
                  :total-visible="7"
                  @input="page_move()"
                ></v-pagination>
              </div>

              <template v-if="layout == 0">
                <v-row>
                  <v-col cols="6" sm="3" v-for="(obj, i) in results.hits.hits" :key="'result_'+i">
                    <v-card>
                      <a target="_blank" :href="obj._related[0]">
                        <v-img :src="obj._thumbnail[0]" contain style="max-height : 200px;" class="grey lighten-2"></v-img>
                      </a>
                      <v-card-text>
                        <a :href="obj._related[0]" target="_blank">
                          <b>{{obj.Title[0]}}</b>
                        </a>
                      </v-card-text>
                    </v-card>
                  </v-col>
                </v-row>
              </template>

              <template v-else>
                <v-card class="my-5" v-for="(obj, i) in results.hits.hits" :key="'result_'+i">
                  <v-card-text>
                    <v-row>
                      <v-col cols="12" sm="3">
                        <a target="_blank" :href="obj._related[0]">
                          <v-img :src="obj._thumbnail[0]" contain style="max-height : 200px;" class="grey lighten-2"></v-img>
                        </a>
                      </v-col>
                      <v-col cols="12" sm="9">
                        <a :href="obj._related[0]" target="_blank">
                          <b>{{obj.Title[0]}}</b>
                        </a>
                        <v-card-text>
                          <template v-for="(obj2, index2) in obj">
                            <div
                              v-if="index2.indexOf('_') == -1 && index2 != 'Title'"
                              :key="index2"
                            >
                              <b>{{index2}} :</b>
                              {{obj2.join(", ")}}
                            </div>
                          </template>
                        </v-card-text>
                      </v-col>
                    </v-row>
                  </v-card-text>
                </v-card>
              </template>

              <div class="text-center">
                <v-pagination
                  v-model="query.page"
                  :length="pagination_length"
                  :total-visible="7"
                  @input="page_move()"
                ></v-pagination>
              </div>
            </template>
          </v-col>
        </v-row>
      </v-container>
    </v-content>

    <v-footer :dark="true" class="mt-5">
      <v-container>
        <p class="text-center my-5"><a style="color : white;" href="https://github.com/nakamura196/isearch">https://github.com/nakamura196/isearch</a></p>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script>
let facetSize = 50;

import axios from "axios";
export default {
  data: () => ({
    config: {
      u: "",
      header: "",
      itemsSort: {}
    },
    query: {
      query: {},
      aggs: {},
      size: 50,
      from: 0,
      page: 1,
      sort: "Title Asc"
    },
    advancedSearch: {},
    advancedSearchDisplay: {},
    facetSearch: {},
    index: {}, //インデックス
    dataAll: [], //検索結果全数
    dataFiltered: [], //検索結果数
    results: [], //ページで分けた数

    facets: {}, // ****,

    layout: 0
  }),
  created() {
    // ------------

    let param = this.$route.query;

    if (!param.u) {
      return;
    }

    this.config.u = param.u;

    axios.get(param.u).then(response => {
      let collection = response.data;

      this.config.header = collection.label ? collection.label : "IIIF Collection Search";

      let results = [];

      let manifests = collection.manifests;

      let pos = 1;

      let index = this.index;

      for (let i = 0; i < manifests.length; i++) {
        let manifest = manifests[i];

        let obj = {
          _thumbnail: [manifest.thumbnail],
          _id: [manifest["@id"]],
          Title: [manifest.label]
        };

        let related;
        if(manifest.related){
          related = manifest.related
        } else {
          related = "http://codh.rois.ac.jp/software/iiif-curation-viewer/demo/?manifest=" + encodeURIComponent(manifest["@id"])
          //related = "https://www.kanzaki.com/works/2016/pub/image-annotator?u=" + manifest["@id"]
        }
        obj._related = [related]

        if (manifest.description) {
          obj.Description = [manifest.description];
        }
        let metadata = manifest.metadata;
        if (metadata) {
          for (let k = 0; k < metadata.length; k++) {
            let m = metadata[k];
            //全て配列に
            let values = m.value;
            if (!(values instanceof Array)) {
              values = [values];
            }
            obj[m.label] = values;
          }
        }

        let fulltext = "";
        let pos_index = pos - 1;

        for (let key in obj) {
          if (!index[key]) {
            index[key] = {};
          }

          let values = obj[key];

          for (let j = 0; j < values.length; j++) {
            let value = values[j];

            //URIの場合は無視
            if (value == null || value.startsWith("http")) {
              continue;
            }

            if (!index[key][value]) {
              index[key][value] = [];
            }

            index[key][value].push(pos_index);

            fulltext += value + " ";
          }
        }

        let key = "Full text search";

        if (!index[key]) {
          index[key] = {};
        }

        if (!index[key][fulltext]) {
          index[key][fulltext] = [];
        }

        index[key][fulltext].push(pos_index);

        results.push(obj);

        pos += 1;
      }

      this.index = index;

      let op = [];

      let itemsSort = {};

      for (let key in index) {
        if (key.indexOf("_") != -1) {
          continue;
        }

        itemsSort[key + " Asc"] = {
          value: key,
          type: "asc"
        };
        itemsSort[key + " Desc"] = {
          value: key,
          type: "desc"
        };

        this.facetSearch[key] = [];

        op.push({
          label: key,
          field: key + ".keyword"
        });
      }

      this.config.itemsSort = itemsSort;

      this.dataAll = results;

      let aggs = {};
      for (let i = 0; i < op.length; i++) {
        let obj = op[i];
        aggs[obj.label] = {
          terms: {
            field: obj.field,
            order: {
              _count: "desc"
            },
            size: facetSize
          }
        };
      }
      this.query.aggs = aggs;

      if (param.advanced) {
        this.advancedSearch = JSON.parse(param.advanced);
      }

      if (param.facet) {
        this.facetSearch = JSON.parse(param.facet);
      }

      if (param.layout) {
        this.layout = Number(param.layout);
      }

      if (param.sort) {
        this.query.sort = param.sort;
      }

      if (param.size) {
        this.query.size = Number(param.size);
      }

      this.search(true);
    });
  },
  methods: {
    search(reindexing_flg) {
      window.scrollTo(0, 0);      

      if (reindexing_flg) {

        //先頭ページに戻る
        this.query.from = 0;
        this.query.page = 1;

        let query = this.createQuery();
        this.query = query;

        let indexes = this.filter(this.query);

        let dataFiltered = this.getDataFiltered(indexes);
        this.dataFiltered = dataFiltered;

        let facets = this.createFacets(indexes, this.query.aggs);
        this.facets = facets;
      }

      this.dataFiltered = this.sort_data(this.dataFiltered, this.query.sort);

      let results = this.getResult(
        this.dataFiltered,
        (this.query.page - 1) * this.query.size,
        this.query.size
      );

      let result = {
        aggregations: this.facets,
        hits: {
          hits: results,
          total: {
            relation: this.query.sort,
            value: this.dataFiltered.length
          }
        }
      };

      for (let key in this.advancedSearch) {
        this.advancedSearchDisplay[key] = this.advancedSearch[key];
      }
      this.update_param();

      this.results = result;
    },
    createQuery() {
      let query = {};
      let filter_query = [];
      let must_query = [];
      query.bool = {
        filter: filter_query,
        must: must_query
      };

      for (let key in this.advancedSearch) {
        let value_advanced = this.advancedSearch[key];
        if (value_advanced != "") {
          filter_query.push(this.createMustQuery(key, [value_advanced], false));
        }
      }

      for (let key in this.facetSearch) {
        let value_facet = this.facetSearch[key];
        if (value_facet.length != 0) {
          filter_query.push(this.createFilterQuery(key, value_facet));
        }
      }

      //------------

      let q = this.query;
      q.query = query;

      return q;
    },
    createMustQuery(field, values, keyword_flg) {
      let should = [];

      for (let i = 0; i < values.length; i++) {
        let value = values[i];
        if (value == "") {
          //注意
          continue;
        }
        let obj = {};
        if (keyword_flg) {
          field = field + ".keyword";
        }
        obj[field] = value;
        should.push({
          match_phrase: obj
        });
      }

      return {
        bool: {
          should: should
        }
      };
    },
    createFilterQuery(field, values) {
      let should = [];

      for (let i = 0; i < values.length; i++) {
        let value = values[i];
        if (value == "") {
          //注意
          continue;
        }
        let obj = {};
        obj[field + ".keyword"] = value;
        should.push({
          match_phrase: obj
        });
      }

      return {
        bool: {
          should: should
        }
      };
    },
    getDataFiltered(indexes) {
      let dataFiltered = [];
      for (let i = 0; i < indexes.length; i++) {
        dataFiltered.push(this.dataAll[indexes[i]]);
      }
      return dataFiltered;
    },
    sort_data(dataFiltered, type) {
      let obj = this.config.itemsSort[type];

      let asc_flg = true;
      if (obj.type == "desc") {
        asc_flg = false;
      }

      let field = obj.value;

      let v_1 = 1;
      let v_2 = -1;
      if (!asc_flg) {
        v_1 *= -1;
        v_2 *= -1;
      }

      let key = "Title";

      dataFiltered.sort(function(a, b) {
        if (a[field][0] > b[field][0]) return v_1;
        if (a[field][0] < b[field][0]) return v_2;
        if (a[key][0] > b[key][0]) return v_1;
        if (a[key][0] < b[key][0]) return v_2;
        return 0;
      });
      return dataFiltered;
    },
    getResult(indexes, from, size) {
      let results = [];
      let to = from + size;
      if (to > this.dataFiltered.length) {
        to = this.dataFiltered.length;
      }
      for (let i = from; i < to; i++) {
        results.push(this.dataFiltered[i]);
      }
      return results;
    },
    createFacets(indexes, query_aggs) {
      let aggs = {};

      for (let label in query_aggs) {
        let obj = query_aggs[label].terms;
        let size = Number(obj.size);
        let field = obj.field.replace(".keyword", "");
        let map = this.index[field];

        let map_new = {};
        for (let value in map) {
          let intersection = new Set(
            [...new Set(indexes)].filter(e => new Set(map[value]).has(e))
          );
          let doc_count = intersection.size;
          if (doc_count > 0) {
            map_new[value] = doc_count;
          }
        }

        //オブジェクトに変換
        let arr = Object.keys(map_new).map(e => ({
          key: e,
          value: map_new[e]
        }));

        //値でそーと
        arr.sort(function(a, b) {
          if (a.value < b.value) return 1;
          if (a.value > b.value) return -1;
          return 0;
        });

        if (size > arr.length) {
          size = arr.length;
        }

        let buckets = [];
        for (let i = 0; i < size; i++) {
          let key = arr[i].key;
          let bucket = {
            key: key,
            doc_count: arr[i].value
          };
          //検索条件の反映
          if (!this.facetSearch[field]) {
            this.facetSearch[field] = [];
          }
          if (this.facetSearch[field].indexOf(key) != -1) {
            bucket.value = true;
          }
          buckets.push(bucket);
        }

        aggs[label] = {
          buckets: buckets
        };
      }

      return aggs;
    },
    filter(query) {
      let index = this.index;

      let index_all = [];
      for (let i = 0; i < this.dataAll.length; i++) {
        index_all.push(i);
      }

      let filters = query.query.bool;

      let intersection = new Set(index_all);

      for (let type in filters) {
        //must or filter
        let type_arr = filters[type];

        for (let i = 0; i < type_arr.length; i++) {
          let should = type_arr[i].bool.should;

          let union = new Set([]);

          for (let j = 0; j < should.length; j++) {
            let obj = should[j]["match_phrase"];

            for (let key in obj) {
              let value = obj[key];

              let index_arr = [];

              if (key.indexOf(".keyword") == -1) {
                let map = index[key];
                for (let field in map) {
                  if (field.toLowerCase().indexOf(value.toLowerCase()) != -1) {
                    index_arr = index_arr.concat(map[field]);
                  }
                }
              } else {
                key = key.replace(".keyword", "");
                let map = index[key];
                for (let field in map) {
                  if (field.toLowerCase() == value.toLowerCase()) {
                    index_arr = index_arr.concat(map[field]);
                  }
                }
              }

              let set_add = new Set(index_arr);
              union = new Set([...union, ...set_add]);
            }
          }

          intersection = new Set([...intersection].filter(e => union.has(e))); //2, 3
        }
      }

      let results = [];

      for (var value of intersection) {
        results.push(value);
      }

      return results;
    },
    page_move() {
      this.search();
    },
    sort_move() {
      this.search();
    },
    size_move() {
      this.search(true);
    },
    //詳細検索ボタン
    search_move() {
      for (let key in this.facetSearch) {
        let value = this.facetSearch[key];
        if (value instanceof Array) {
          value = [];
        } else {
          value = "";
        }
        this.facetSearch[key] = value;
      }

      if (this.query.page != 1) {
        this.query.page = 1;
        this.sort = "Title Asc";
      }
      this.search(true);
    },
    update_param() {
      let param = {
        u: this.config.u,
        advanced: JSON.stringify(this.advancedSearch),
        facet: JSON.stringify(this.facetSearch),
        layout: this.layout,
        size: this.query.size,
        sort: this.query.sort
      };
      this.$router.replace({ query: param }, () => {}, () => {});
    },
    init_param() {
      this.query.query = {};
      this.query.size = 50;
      this.query.from = 0;
      this.query.page = 1;
      this.query.sort = "Title Asc";

      for (let key in this.advancedSearch) {
        let value = this.advancedSearch[key];
        if (value instanceof Array) {
          value = [];
        } else {
          value = "";
        }
        this.advancedSearch[key] = value;
      }

      for (let key in this.facetSearch) {
        let value = this.facetSearch[key];
        if (value instanceof Array) {
          value = [];
        } else {
          value = "";
        }
        this.facetSearch[key] = value;
      }

      this.update_param();
    },
    reset() {
      this.init_param();
      this.search(true);
    },
    facet_filter() {
      //list値の初期化
      for (let key in this.facetSearch) {
        let value = this.facetSearch[key];
        if (value instanceof Array) {
          value = [];
        } else {
          value = "";
        }
        this.facetSearch[key] = value;
      }

      let aggregations = this.results.aggregations;
      for (let field in aggregations) {
        let buckets = aggregations[field].buckets;
        for (let i = 0; i < buckets.length; i++) {
          let bucket = buckets[i];
          if (bucket.value) {
            if (!this.facetSearch[field]) {
              this.facetSearch[field] = [];
            }
            this.facetSearch[field].push(bucket.key);
          }
        }
      }
      this.search(true);
    }
  },
  watch: {
    layout: function() {
      this.update_param();
    }
  },
  computed: {
    // 算出 getter 関数
    total: function() {
      let total = 0;
      if (this.results.hits) {
        total = this.results.hits.total.value;
      }
      return total;
    },
    pagination_length: function() {
      return Math.ceil(this.total / this.query.size);
    },
    computed_itemsSort: function() {
      let arr = [];
      for (let key in this.config.itemsSort) {
        arr.push(key);
      }
      return arr;
    }
  }
};
</script>
<style>
.v-btn {
  text-transform: none !important;
}
</style>
