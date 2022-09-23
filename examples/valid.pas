var i: integer := 1;
var r := 2.5;

begin
  var s: real := 1.0;
  for j: integer := 1 to 10 do
    s += j;

  var p := 1;

  for var j := 1 to 10 do
    p *= j;

  var str := '';
  for c: char := 'a' to 'z' do
    str += c;

end.
