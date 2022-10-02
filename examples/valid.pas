var i: integer := 1;
var r: real := 2.5;

begin
  var s: real := 1.0;
  for var j: integer := 1 to 10 do
    s += j;

  var p: integer := 1;

  for var j: integer := 1 to 10 do
    p *= j;

  var str: string := '';
  for var c: char := 'a' to 'z' do
    str += c;

end.
