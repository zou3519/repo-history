import re
import os


def HUSLPercentile(model, metricDict):
    """
        Assigns edit ids in model to colors by percentile based on
            metricDict. Returns a dictionary of colors.
    """
    print("Assigning colors . . .")

    # Sort by decreasing scores
    a = [(metricDict[x[1]], x[1]) for x in model]
    s = set(a)
    a = sorted(list(s), reverse=True)

    # Assign colors to nodes
    length = len(a)

    colors = {}

    for i in range(int(length * 0.2)):
        colors[a[i][1]] = "c0"

    for i in range(int(length * 0.2), int(0.4 * length)):
        colors[a[i][1]] = "c1"

    for i in range(int(length * 0.4), int(length * 0.6)):
        colors[a[i][1]] = "c2"

    for i in range(int(length * 0.6), int(length * 0.8)):
        colors[a[i][1]] = "c3"

    for i in range(int(length * 0.8), int(length)):
        colors[a[i][1]] = "c4"

    return colors


def beginning_whitespace(string):
    whitespace_matcher = re.compile(r'^\s+')
    match = whitespace_matcher.search(string)
    return '' if match is None else match.group(0)


def whitespace2html(whitespace):
    result = ''
    for char in whitespace:
        if char == ' ':
            result += '&nbsp'
        elif char == '\t':
            result += 8 * '&nbsp'
    return result


def colorHUSL(title, remove, metricName, model, content, colors, metricDict):
    """
        Writes the most recent revision to a .html file based on the dictionary
            colors.
        metricName will be part of the file title
    """
    print ("Writing heat map . . .")

    if not os.path.isdir('heatmaps'):
        os.mkdir('heatmaps')

    if remove:
        colorFile = open("heatmaps/" + (metricName + "_" +
                                        title).replace(" ", "_") + "_rem.html", "w")
    else:
        colorFile = open("heatmaps/" + (metricName + "_" +
                                        title).replace(" ", "_") + ".html", "w")

    # Write style sheet
    colorFile.write("<!DOCTYPE html>\n<html>\n<head>\n<style/>\n")
    colorFile.write(
        ".c0 {\n\tbackground-color: #d7191c;\n\tcolor: black;\n}\n")
    colorFile.write(
        ".c1 {\n\tbackground-color: #fdae61;\n\tcolor: black;\n}\n")
    colorFile.write(
        ".c2 {\n\tbackground-color: #ffffbf;\n\tcolor: black;\n}\n")
    colorFile.write(
        ".c3 {\n\tbackground-color: #abdda4;\n\tcolor: black;\n}\n")
    colorFile.write(".c4 {\n\tbackground-color: #2b83ba;\n\tcolor: black;}\n")

    # For code analysis: comment out if necessary
    code = True
    if code:
        colorFile.write(
            "p {\n\tfont-family: \"Courier New\", Courier, monospace;\n\tline-height: 20%;\n}\n")

    colorFile.write("</style>\n</head>\n")

    # Write content
    colorFile.write("<body>\n")

    content = content.split("\n")
    # content = [(line.split(), whitespace2html(beginning_whitespace(line))) for line in content]
    content = [([line], whitespace2html(beginning_whitespace(line))) for line in content]
    print(content)
    # content = [re.split(r'(\s+)', line) for line in content]
    # print content

    pos = 0
    dif = model[pos][0]
    color = colors[model[pos][1]]

    def tooltip(pos):
        pid = model[pos][1]
        score = metricDict[pid]
        return "'%d: %d'" % (pid, score)

    for (line, starting_whitespace) in content:
        current = "<p><span title=%s class=%s>%s" % (tooltip(pos), color, starting_whitespace if code else '')
        for word in line:
            if dif == 0:
                while dif == 0:
                    pos += 1
                    color = colors[model[pos][1]]
                    dif = model[pos][0] - model[pos - 1][0]
                current += "</span><span title=%s class=%s>" % (tooltip(pos), color)

            if word == '':
                current += '&nbsp'

            current += "%s " % word
            dif -= 1
        current += "</span></p>\n"
        colorFile.write(current)

    colorFile.write("</body>\n</html>")
    colorFile.close()


def build_heatmap(name, model, content, score_dict):
    colors = HUSLPercentile(model, score_dict)
    colorHUSL(name, False, name, model, content, colors, score_dict)
