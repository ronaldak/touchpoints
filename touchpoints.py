# MIT License
#
# Copyright (c) 2018 Ronald Klazar
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import json
import os

class MarkdownBuilder(object):
	class Phrase(object):
		def __init__(self, phrase):
			self.phrase = phrase

	class Heading(Phrase):
		def __init__(self, phrase):
			MarkdownBuilder.Phrase.__init__(self, phrase)

		def __str__(self):
			return self.phrase + '\n' + ('=' * len(self.phrase)) + '\n'

	class Subheading(Phrase):
		def __init__(self, phrase):
			MarkdownBuilder.Phrase.__init__(self, phrase)

		def __str__(self):
			return '## ' + self.phrase

	class BoldPhrase(Phrase):
		def __init__(self, phrase):
			MarkdownBuilder.Phrase.__init__(self, phrase)

		def __str__(self):
			return '**' + self.phrase + '**'

	class ItalicsPhrase(Phrase):
		def __init__(self, phrase):
			MarkdownBuilder.Phrase.__init__(self, phrase)

		def __str__(self):
			return '_' + self.phrase + '_'

	class MonospacePhrase(Phrase):
		def __init__(self, phrase):
			MarkdownBuilder.Phrase.__init__(self, phrase)

		def __str__(self):
			return '`' + self.phrase + '`'

	class HorizontalRule(Phrase):
		def __init__(self):
			MarkdownBuilder.Phrase.__init__(self, None)

		def __str__(self):
			return '\n---\n'

	class Line(object):
		def __init__(self, phrases=[]):
			self.phrases = phrases

		def __str__(self):
			result = ''

			for phrase in self.phrases:
				result += (' ' if len(result) > 0 else '') + str(phrase)

			return result + '\n'

	def __init__(self):
		self.lines = []

	def addLine(self, line):
		self.lines.append(line)

	def __str__(self):
		result = ''

		for line in self.lines:
			result += str(line)

		return result;

def parseCommandLineArguments():
	parser = argparse.ArgumentParser(description='Index touchpoints in a source tree')
	parser.add_argument('marker', help='A string representing the touchpoint marker')
	parser.add_argument('root', help='The root directory where the source files to search are located')
	parser.add_argument('extensions', nargs='*', help='Extensions of the files to search (e.g. .js .py)')
	parser.add_argument('description_file', help='Path to touchpoint description file')
	parser.add_argument('output_file', default=None, help='Path to output file in Markdown format')
	return vars(parser.parse_args())

def parseDescriptionFile(descriptionFile):
	descriptions = {}

	if descriptionFile is not None:
		with open(descriptionFile, 'rt') as df:
			descriptions = json.load(df)
	
	return descriptions

def writeDescriptionFile(descriptions, descriptionFile):
	with open(descriptionFile, 'wt') as df:
		json.dump(descriptions, df, indent=2)

def updateDescriptions(root, extensions, marker, descriptions):
	touchpoints = {}

	for root, directories, files in os.walk(root):
		for file in files:
			name, extension = os.path.splitext(file)

			if extension in extensions:
				touchpoints = findTouchpoints(marker, os.path.join(root, file), touchpoints)

	missingTouchpointNames = []
	touchpointNames = []

	for touchpointName in descriptions.keys():
		if touchpointName in touchpoints:
			touchpointNames.append(touchpointName)
		else:
			missingTouchpointNames.append(touchpointName)

	for touchpointName in touchpoints.keys():
		if touchpointName not in descriptions:
			touchpointNames.append(touchpointName)

	missingTouchpointNames.sort()
	touchpointNames.sort()

	newDescriptions = {}

	for touchpointName in missingTouchpointNames:
		newDescriptions[touchpointName] = {
			'description': descriptions[touchpointName]['description'],
			'missing': True
		}

	for touchpointName in touchpointNames:
		newDescriptions[touchpointName] = {
			'description': descriptions[touchpointName]['description'] if touchpointName in descriptions else '',
			'locations': touchpoints[touchpointName] if touchpointName in touchpoints else []
		}

	return newDescriptions

def findTouchpoints(marker, file, touchpoints = {}):
	contents = None

	try:
		with open(file, 'rt') as f:
			contents = f.read()

		markerIndex = 0
		more = True

		while more:
			try:
				markerIndex = contents.index(marker, markerIndex)
				newlineIndex = markerIndex

				while newlineIndex < len(contents) and contents[newlineIndex] != '\n':
					newlineIndex += 1

				touchpointName = contents[markerIndex + len(marker):newlineIndex].strip()
				touchpointLocation = {
					'file': file,
					'line': countLines(contents, markerIndex) + 1
				}

				if touchpointName not in touchpoints:
					touchpoints[touchpointName] = []
				touchpoints[touchpointName].append(touchpointLocation)

				markerIndex = newlineIndex + 1
			except:
				more = False
	except UnicodeDecodeError:
		print('Skipping possible binary file: ' + file)
	except Exception as exception:
		print('Unable to read file: ' + file)
		print('\t' + str(exception))

	return touchpoints

def countLines(buffer, endIndex):
	count = 0
	i = 0

	while i < endIndex and i < len(buffer):
		if buffer[i] == '\n':
			count += 1
		i += 1

	return count

def writeOutputFile(descriptions, outputFile):
	builder = MarkdownBuilder()

	def addTouchpoint(name, description):
		builder.addLine(MarkdownBuilder.Line([MarkdownBuilder.Subheading(name)]))
		builder.addLine(MarkdownBuilder.Line([MarkdownBuilder.ItalicsPhrase(description if len(description) > 0 else '(No description.)')]))

	builder.addLine(MarkdownBuilder.Line([MarkdownBuilder.Heading("Touchpoints")]))

	missingTouchpoints = [ { 'name': name, 'description': touchpoint['description'] } for name, touchpoint in descriptions.items() if 'missing' in touchpoint and touchpoint['missing'] ]

	if len(missingTouchpoints) > 0:
		for touchpoint in missingTouchpoints:
			addTouchpoint('[Missing] ' + touchpoint['name'], touchpoint['description'])

		builder.addLine(MarkdownBuilder.Line([MarkdownBuilder.HorizontalRule()]))

	for touchpointName, touchpoint in descriptions.items():
		if 'missing' not in touchpoint or touchpoint['missing'] is False:
			addTouchpoint(touchpointName, touchpoint['description'])

			builder.addLine(MarkdownBuilder.Line());
			for location in touchpoint['locations']:
				builder.addLine(MarkdownBuilder.Line([MarkdownBuilder.MonospacePhrase(location['file'] + ":" + str(location['line']))]))
				builder.addLine(MarkdownBuilder.Line());

	with open(outputFile, 'wt') as of:
		of.write(str(builder))

def main():
	args = parseCommandLineArguments()

	descriptions = parseDescriptionFile(args['description_file'])
	descriptions = updateDescriptions(args['root'], args['extensions'], args['marker'], descriptions)
	writeDescriptionFile(descriptions, args['description_file'])

	if (args['output_file'] is not None):
		writeOutputFile(descriptions, args['output_file'])

if __name__ == '__main__':
    main()
