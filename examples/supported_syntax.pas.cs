using System;

namespace Transpiler
{
    internal class Program
    {
        static int var1 = ((1 + 2) * 3) - 4;
        static double var2 = 0 + (2.7 - 1.2) / 1;
        static char var3 = 'c';
        static string var4 = "some string1";
        static bool var5 = true;

        public static void Main(string[] args)
        {
            int int_var = 0;
            var1 = 1;
            var1 = 1;
            var1 = int_var + 1;
            var2 = 0.5;
            if (var1 > 1)
                Console.WriteLine("var1 > 1");
            if ((var2 < 5) || (var5))
            {
                var5 = false;
            }
            if ((false))
                Console.Write("false");
            else
                Console.Write("else");
            if ((var4 == "a"))
            {
                Console.Write("a");
            }
            else if ((var4 == "b"))
            {
                Console.Write("b");
            }
            else
                Console.Write("unknown");
            for (int i = 1; i <= 3; i++)
            {
                var1 = 1;
                var3 = 'a';
            }
            for (int j = 3; j >= 1; j--)
                var1 = 1;
            while (var1 <= 1)
                var1 = 1;
            do {
                var1 = 1;
            } while (true);
            var1 = Math.Abs(-1);
            double var_sqr = Math.Pow(2, 4);
            double var_sqrt = Math.Sqrt(4.0);
            double var_exp = Math.Exp(-2);
        }

    }
}
