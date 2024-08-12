const $addQ = $("#add-question")
$addQ.on("click", addQuestion)

function addQuestion() {
    const nextQNum = $("#add-survey-form fieldset").length + 1
    $addQ.before(`
        <fieldset id="question-group${nextQNum}">
            <legend>Question ${nextQNum}</legend>
            <label for="q${nextQNum}">Question:</label>
            <input type="text" name="q${nextQNum}" id="q${nextQNum}">
            <br>
            <label for="choice${nextQNum}">Choice:</label>
            <input type="text" name="choice${nextQNum}" id="choice${nextQNum}" placeholder="ie. Yes, No. Choices must be separated by commas. If not provided, default values are Yes and No.">
            <br>
            <label for="comment${nextQNum}">Allow comments?</label>
            <input type="checkbox" name="comment${nextQNum}" id="comment${nextQNum}">
        </fieldset>
        `)
}