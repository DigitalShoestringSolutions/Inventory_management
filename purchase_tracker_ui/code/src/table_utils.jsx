import React from "react"
import { Pagination } from "react-bootstrap"


export function groupBy(xs, key) {
  return xs.reduce(function (rv, x) {
    (rv[x[key]] = rv[x[key]] || []).push(x);
    return rv;
  }, {});
};

export function pivot(arr) {
  let out = [];
  let j_length = arr.reduce((acc, item) => item.length > acc ? item.length : acc, 0)
  for (let i = 0; i < arr.length; i++) {
    for (let j = 0; j < j_length; j++) {
      out[j] = out[j] ?? []
      out[j][i] = arr[i][j]
    }
  }
  return out;
}

export function PaginateWidget({ active, n_pages, setPage }) {
  const [scroll, doSetScroll] = React.useState(1)
  const show_limit = 8

  //defaults: n_pages <= show_limit - show all normally
  let pages_shown = n_pages
  let show_prev = false
  let prev_active = false
  let prev_ellipsis = false
  let next_ellipsis = false
  let next_active = false
  let show_next = false

  if (n_pages > show_limit) {
    pages_shown = show_limit - 4
    show_prev = true
    prev_ellipsis = true
    next_ellipsis = true
    show_next = true

    if (scroll < 3) {
      show_prev = false
      pages_shown++
      prev_ellipsis = false
      pages_shown++
    }

    if (scroll > active) {
      prev_active = true
      pages_shown--
    }

    if (scroll > n_pages - pages_shown - 2) {
      show_next = false
      pages_shown++
      next_ellipsis = false
      pages_shown++
    } else if (scroll + pages_shown <= active) {
      next_active = true
      pages_shown--

      // if(scroll + pages_shown === active -1)
      // {
      //   next_ellipsis = false
      //   pages_shown++
      // }
    }
  }


  const setScroll = (n) => {
    if (n === +1 && scroll < 4) {
      doSetScroll(5)
      return
    }
    if (n === -1 && scroll === 5) {
      doSetScroll(1)
      return
    }

    if (n === +1 && active === scroll) {
      n = +2
    }

    if (n === +1 && scroll + pages_shown === active - 1) {
      n = +1
    }

    if (n === -1 && active === scroll - 2) {
      n = -2
    }
    // if (n >= 1 && n <= n_pages - show_limit + 1)
    doSetScroll(scroll + n)
  }

  let pages = Array.from({ length: pages_shown }, (_, i) => i + scroll)

  return <div className="d-flex justify-content-center mt-1 mb-1">
    <Pagination size="sm" className='mb-0'>
      {show_prev ? <Pagination.Prev onClick={() => setScroll(-1)} /> : ""}
      {prev_active ? <Pagination.Item key={active} active={true}>{active}</Pagination.Item> : ""}
      {prev_ellipsis ? <Pagination.Ellipsis /> : ""}
      {pages.map(number => (<Pagination.Item key={number} active={number === active} onClick={() => setPage(number)}>{number}</Pagination.Item>))}
      {next_ellipsis ? <Pagination.Ellipsis /> : ""}
      {next_active ? <Pagination.Item key={active} active={true}>{active}</Pagination.Item> : ""}
      {show_next ? <Pagination.Next onClick={() => setScroll(+1)} /> : ""}
    </Pagination>
  </div>
}

export function paginate(array, page_size, page_number) {
  // human-readable page numbers usually start with 1, so we reduce 1 in the first argument
  return array.slice((page_number - 1) * page_size, page_number * page_size);
}