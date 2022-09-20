$(document).ready(function () {
    get_posts()
})

function toggle_like(term_id) {
    console.log(term_id)
    let $a_like = $(`#${term_id} a[aria-label='bookmark']`)
    let $i_like = $a_like.find("i")
    if ($i_like.hasClass("fa-bookmark")) {
        $.ajax({
            type: "POST",
            url: "/update_bookmark",
            data: {
                term_id_give: term_id,
                action_give: "unlike"
            },
            success: function (response) {
                console.log("unlike")
                $i_like.addClass("fa-bookmark-o").removeClass("fa-bookmark")
            }
        })
    } else {
        $.ajax({
            type: "POST",
            url: "/update_like",
            data: {
                term_id_give: term_id,
                action_give: "like"
            },
            success: function (response) {
                console.log("like")
                $i_like.addClass("fa-bookmark").removeClass("fa-bookark-o")
            }
        })

    }
}

function post() {
    let term = $("#term").val()
    let definition = $("#definition").val()
    $.ajax({
        type: "POST",
        url: "/posting",
        data: {
            term_give: term,
            definition_give: definition
        },
        success: function (response) {
            window.location.reload()
        }
    })
}

function get_posts() {
    $("#tbody-box").empty()
    $.ajax({
        type: "GET",
        url: "/get_posts",
        data: {},
        success: function (response) {
            console.log(response)
            if (response["result"] == "success") {
                let terms = response["terms"]
                for (let i = 0; i < terms.length; i++) {
                    let term = terms[i]
                    // 삼항 연산자
                    let class_bookmark = term['bookmark_by_me'] ? "fa-bookmark" : "fa-bookmark-o"
                    // class_heart 값은 ? 앞의 첫째 항의 boolean 값이 true 면 2번째 항, false 면 3번째 항이 된다.
                    let html_temp = `<tr id="${term['_id']}">
                                        <td><a href="#">${term['term']}</a></td>
                                        <td>${term['definition']} 
                                        </td>
                                     </tr>
                                    <a class="level-item is-sparta" aria-label="heart" onclick="toggle_like('${post['_id']}', 'heart')">
                                        <span class="icon is-small"><i class="fa fa-heart" aria-hidden="true"></i></span>
                                    </a>`

                    $("#tbody-box").append(html_temp)
                }
            }
        }
    })
}


