// TEAM CARROSEL
const slideBox = $('#teambox .container-team');
const teamNodes = [];

$.each($('.person'), (index, el) => teamNodes.push(el));

const cardSize = $('.person').width();
const firstSlide = 0;

const btnNext = $('#btnNext');
const btnPrev = $('#btnPrev');

// handle infinite next slides
function nextMember() {
    $(teamNodes[firstSlide]).children('.title').animate({
        opacity: 0
    }, 200);

    $(teamNodes[firstSlide]).animate({
        width: 0,
    }, 400, function() {
        $(teamNodes[firstSlide]).children('.title').animate({ opacity: 1});
        // remove dom element
        $(teamNodes[firstSlide]).remove();

        // change element position for last of array
        const el = teamNodes.shift();
        teamNodes.push(el);
        // put last node in DOM again
        $(teamNodes[teamNodes.length - 1]).css('width', cardSize);
        slideBox.append(teamNodes[teamNodes.length - 1]);

    });
};

// handle infinite previos slides
function prevMember() {
    $(teamNodes[teamNodes.length - 1]).css('width', 0);

    $(teamNodes[teamNodes.length - 1]).remove();

    const el = teamNodes.pop();
    teamNodes.unshift(el);
    slideBox.prepend(teamNodes[firstSlide]);
    $(teamNodes[firstSlide]).animate({
        width: cardSize,
    }, 400, function() {

    });
};

btnNext.click(() => nextMember());
btnPrev.click(() => prevMember());

setInterval(() => nextMember(), 4000);
