var
    var1: integer := ((1 + 2) * 3) - 4;
    var2: real := 0 + (2.7 - 1.2) / 1;
    var3: char := 'c';
    var4: string := 'some string1';

var var5: boolean := true;

begin

var1 += 1;
var1 -= 1;
var1 *= 1;
var2 /= 0.5;

if (var1 > 1) then
    println('var1 > 1');

if (var2 < 5) or (var5) then
begin
    var5 := false;
end;

for var i: integer := 1 to 3 do
begin
    var1 += 1;
end;

for var j: integer := 3 downto 1 do
    var1 -= 1;

while var1 <= 1 do
    var1 *= 1;

repeat
    var1 += 1;
until true;

var var_abs := abs(-1);
var var_sqr := sqr(2);
var var_sqrt := sqrt(4.0);
var var_exp := exp(2);

end.
